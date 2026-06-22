from multiprocessing.managers import rebuild_as_list

from fastapi import FastAPI , HTTPException , File,UploadFile, Form ,Depends
from pycparser.ast_transforms import fix_atomic_specifiers

from app.schema import PostCreate,PostResponse,UserRead,UserCreate,UserUpdate
from app.db import Post,create_db_and_tables,get_async_session,User
from sqlalchemy.ext.asyncio import AsyncSession, result
from contextlib import asynccontextmanager
from sqlalchemy import select, true
from app.images import imagekit
from pathlib import Path
import shutil
import os
import uuid
import tempfile
from app.users import auth_backend,current_active_user,fastapi_users


@asynccontextmanager
async def lifespan(app:FastAPI):
    await create_db_and_tables()
    yield
app = FastAPI(lifespan=lifespan)

app.include_router(fastapi_users.get_auth_router(auth_backend),prefix="/auth/jwt",tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserRead,UserCreate),prefix='/auth',tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(),prefix='/auth',tags=["auth"])
app.include_router(fastapi_users.get_verify_router(UserRead),prefix='/auth',tags=["auth"])
app.include_router(fastapi_users.get_users_router(UserRead,UserUpdate),prefix='/users',tags=["users"])


@app.post('/upload')
async def upload_file(
        file: UploadFile = File(...),
        caption: str = Form(''),
        user:User=Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session)
):
    temp_file_path = None
    try:
        # Reset pointer
        await file.seek(0)

        # Create temp file
        suffix = os.path.splitext(file.filename)[1] if file.filename else ""
        # mkstemp returns a tuple (fd, path), we only need the path
        temp_file_path = tempfile.mkstemp(suffix=suffix)[1]

        # Write content
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. CRITICAL FIX: Convert string path to Path object
        upload_result = imagekit.files.upload(
            file=Path(temp_file_path),  # Pass Path object, NOT string
            file_name=file.filename,
            use_unique_file_name=True,
            tags=['backend-upload']
        )

        post = Post(
            user_id=user.id,
            caption=caption,
            url=upload_result.url,
            file_type='video' if file.filename.lower().endswith(('.mp4', '.mkv')) else 'image',
            file_name=upload_result.name,
        )

        session.add(post)
        await session.commit()
        await session.refresh(post)

        return post

    except Exception as e:
        import traceback
        print(f"Upload Error: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")

    finally:
        if file and hasattr(file, "file"):
            try:
                file.file.close()
            except:
                pass

        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except PermissionError:
                print(f"Warning: Could not delete temp file {temp_file_path}")
@app.get('/feed')
async def get_feed(
    session: AsyncSession=Depends(get_async_session),
    user:User=Depends(current_active_user),
):
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts = [row[0] for row in result.all()]

    rest=await session.execute(select(User))
    users=[row[0] for row in rest.all()]
    user_dict={u.id:u.email for u in users}

    posts_data=[]
    for post in posts:
        posts_data.append(
            {
                "id":str(post.id),
                "user_id":str(post.user_id),
                "caption": post.caption,
                "url":post.url,
                "file_type":post.file_type,
                "file_name":post.file_name,
                "created_at":post.created_at.isoformat(),
                "is_owner":post.user_id == user.id ,
                "email":user_dict.get(post.user_id,'unknown')
            }
        )
    return {"posts":posts_data}
@app.delete('/post/{id}')
async def delete_post(id:str, session: AsyncSession=Depends(get_async_session),user:User=Depends(current_active_user)):
    try:
        post_uuid=uuid.UUID(id)
        result=await session.execute(select(Post).where(Post.id == post_uuid))
        post=result.scalars().first()

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        if post.user_id != user.id:
            raise HTTPException(status_code=403, detail="You do not have permission to perform this action")

        await session.delete(post)
        await session.commit()
        return {"success":True,"message":"Post deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")