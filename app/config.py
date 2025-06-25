import os
import cloudinary
from fastapi.openapi.utils import get_openapi

# Set your Cloudinary credentials
def load_cloudinay_config():
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET")
    )

# config custom_openapi
def custom_openapi(app):
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="FastAPI Messenger API",
        version="0.1.0",
        description="Messenger is a realtime chat backend application created with FastAPI," \
        " MySQL, MongoDB...\nThis api require authorization via JWT",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    for route in app.routes:
        # break part to parts 'api/user/1' = > ['api', 'user', '1']
        path_parts = route.path.strip("/").split("/") 
        # skip the versioning 'api/user/1' => '/user/1'
        sub_path = "/" + "/".join(path_parts[2:])
        if sub_path not in ["/","/docs", "/openapi.json"] and not sub_path.startswith("/auth/"):
            if hasattr(route, "operation_id"):
                path = openapi_schema["paths"][route.path]
                for method in path:
                    path[method]["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema