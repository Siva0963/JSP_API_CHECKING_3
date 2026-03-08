from sqlalchemy import (Column,Integer,String,Text,ForeignKey,Boolean,Date,DateTime,Enum,UniqueConstraint,Index
)

from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import enum
from app.utils.pytz_utils import get_ist_time

Base = declarative_base()

# =====================================================
# STATE
# =====================================================

class State(Base):
    __tablename__ = "states"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    #created_at = Column(DateTime, server_default=func.now())
    districts = relationship("District", back_populates="state", cascade="all, delete")


# =====================================================
# DISTRICT
# =====================================================

class District(Base):

    __tablename__ = "districts"
    id = Column(Integer, primary_key=True)
    state_id = Column(Integer, ForeignKey("states.id", ondelete="CASCADE"))
    name = Column(String(100), nullable=False)
    state = relationship("State", back_populates="districts")
    constituencies = relationship("Constituency", back_populates="district", cascade="all, delete")


# =====================================================
# CONSTITUENCY (Previously Assembly)
# =====================================================

class Constituency(Base):

    __tablename__ = "constituencies"

    id = Column(Integer, primary_key=True)

    district_id = Column(Integer, ForeignKey("districts.id", ondelete="CASCADE"))
    name = Column(String(150), nullable=False)


    district = relationship("District", back_populates="constituencies")

    mandals = relationship("Mandal", back_populates="constituency", cascade="all, delete")


# =====================================================
# MANDAL
# =====================================================

class Mandal(Base):

    __tablename__ = "mandals"

    id = Column(Integer, primary_key=True)

    constituency_id = Column(Integer, ForeignKey("constituencies.id", ondelete="CASCADE"))

    name = Column(String(100), nullable=False)



    constituency = relationship("Constituency", back_populates="mandals")

    panchayats = relationship("Panchayat", back_populates="mandal", cascade="all, delete")


# =====================================================
# PANCHAYAT
# =====================================================

class Panchayat(Base):

    __tablename__ = "panchayats"

    id = Column(Integer, primary_key=True)

    mandal_id = Column(Integer, ForeignKey("mandals.id", ondelete="CASCADE"))

    name = Column(String(100), nullable=False)
    area_category = Column(String(50), nullable=False)
 
    mandal = relationship("Mandal", back_populates="panchayats")

    wards = relationship("Ward", back_populates="panchayat", cascade="all, delete")


# =====================================================
# WARD
# =====================================================

class Ward(Base):
    __tablename__ = "wards"
 
    id = Column(Integer, primary_key=True)
 
    ward_number = Column(Integer, nullable=False)
    name = Column(String(150), nullable=True)
    panchayat_id = Column(Integer, ForeignKey("panchayats.id", ondelete="CASCADE"))
    __table_args__ = (
        UniqueConstraint("panchayat_id", "ward_number"),
        Index("idx_ward_panchayat", "panchayat_id"),
    )
 
    panchayat = relationship("Panchayat", back_populates="wards")
    members = relationship("Member", back_populates="ward")
 
 

# =====================================================
# MEMBER
# =====================================================

class Member(Base):
    __tablename__ = "members"
 
    id = Column(Integer, primary_key=True)
 
    full_name = Column(String(150), nullable=False)
    kriya_id = Column(String(50), unique=True, nullable=False)
    mobile = Column(String(15), unique=True, nullable=False)
    email = Column(String(150), unique=True)
 
    address = Column(Text)
 
    state_id = Column(Integer, ForeignKey("states.id"))
    district_id = Column(Integer, ForeignKey("districts.id"))
    constituency_id = Column(Integer, ForeignKey("constituencies.id"))
    mandal_id = Column(Integer, ForeignKey("mandals.id"))
    panchayat_id = Column(Integer, ForeignKey("panchayats.id"))
    ward_id = Column(Integer, ForeignKey("wards.id"))
 
    is_active = Column(Boolean, default=True)
 
    created_at = Column(DateTime, server_default=func.now())
 
    ward = relationship("Ward", back_populates="members")
    otps = relationship("OTP", back_populates="member", cascade="all, delete")

# =====================================================
# OTP
# =====================================================

class OTP(Base):

    __tablename__ = "otps"

    id = Column(Integer, primary_key=True)

    member_id = Column(
        Integer,
        ForeignKey("members.id", ondelete="CASCADE"),
        nullable=False
    )

    otp_code = Column(String(6), nullable=False)

    expires_at = Column(DateTime, nullable=False)

    is_used = Column(Boolean, default=False)

    created_at = Column(DateTime, default=get_ist_time)

    member = relationship("Member", back_populates="otps")