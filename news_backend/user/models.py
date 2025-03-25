import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    app_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=100)
    dob = models.DateField(null=True, blank=False) 
    gender = models.CharField(max_length=10, choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")])
    country = models.CharField(max_length=50)
    genres_selected = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    def save(self,*args,**kwargs):
        if len (self.genres_selected)>10:
            raise ValueError("You can select upto 10 genres only")
        super().save(*args,**kwargs)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'mobile',"dob", "gender", "country"]

    def get_user_id(self):  # 👈 This is the key part!
        return str(self.uuid)

    class Meta:
        db_table = "user"

    def __str__(self):
        return self.email

