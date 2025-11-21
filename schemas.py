"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

# Example schemas (you can keep these for reference)
class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Handcrafted initiative specific schemas
class Artisan(BaseModel):
    name: str = Field(..., description="Artisan full name")
    craft_type: str = Field(..., description="Type of craft e.g., handloom, pottery")
    region: str = Field(..., description="Region/City/State")
    bio: Optional[str] = Field(None, description="Short bio")
    avatar_url: Optional[str] = Field(None, description="Profile image URL")
    portfolio_images: Optional[List[str]] = Field(default_factory=list, description="Image URLs for products")
    phone: Optional[str] = Field(None, description="Phone or WhatsApp number")
    price_range: Optional[str] = Field(None, description="Typical price range")
    featured: bool = Field(False, description="Whether featured on home page")

class Registration(BaseModel):
    name: str
    craft_type: str
    location: str
    phone: str
    email: Optional[EmailStr] = None
    image1_base64: Optional[str] = Field(None, description="First sample image as base64 (optional)")
    image2_base64: Optional[str] = Field(None, description="Second sample image as base64 (optional)")
    consent: bool = Field(..., description="User consent to store/share info for program outreach")
    source: Optional[str] = Field("website", description="Where this registration came from")
