from fastapi import HTTPException, status


def raise_401_exception():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect Credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def raise_404_exception():
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Requested resource does not exist",
    )
