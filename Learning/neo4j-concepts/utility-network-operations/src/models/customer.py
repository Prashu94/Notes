"""Customer model for utility services."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class CustomerType(str, Enum):
    """Types of utility customers."""
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    MUNICIPAL = "municipal"


class CustomerStatus(str, Enum):
    """Customer account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


@dataclass
class Customer:
    """
    Represents a utility service customer.
    
    Attributes:
        id: Unique customer identifier
        name: Customer name (person or business)
        type: Customer type
        status: Account status
        email: Contact email
        phone: Contact phone
        address: Service address
        city: City
        state: State/province
        postal_code: Postal/ZIP code
        latitude: GPS latitude
        longitude: GPS longitude
        account_created_date: Account creation date
        last_payment_date: Most recent payment date
        current_balance: Outstanding balance
        average_monthly_consumption: Average usage
        total_lifetime_consumption: Total consumption since account creation
        credit_rating: Credit score/rating
        auto_pay_enabled: Whether auto-payment is enabled
        paperless_billing: Whether customer opted for paperless billing
        notes: Additional notes
    """
    
    id: str
    name: str
    type: CustomerType
    status: CustomerStatus
    email: str
    phone: str
    address: str
    account_created_date: datetime
    
    # Optional location details
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Financial information
    last_payment_date: Optional[datetime] = None
    current_balance: float = 0.0
    credit_rating: Optional[str] = None
    
    # Consumption tracking
    average_monthly_consumption: float = 0.0
    total_lifetime_consumption: float = 0.0
    
    # Account preferences
    auto_pay_enabled: bool = False
    paperless_billing: bool = False
    notes: Optional[str] = None
    
    def to_neo4j_properties(self) -> Dict[str, Any]:
        """Convert to Neo4j node properties."""
        props = {
            'id': self.id,
            'name': self.name,
            'type': self.type.value,
            'status': self.status.value,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'account_created_date': self.account_created_date.isoformat(),
            'current_balance': self.current_balance,
            'average_monthly_consumption': self.average_monthly_consumption,
            'total_lifetime_consumption': self.total_lifetime_consumption,
            'auto_pay_enabled': self.auto_pay_enabled,
            'paperless_billing': self.paperless_billing,
        }
        
        # Add optional fields
        if self.city:
            props['city'] = self.city
        if self.state:
            props['state'] = self.state
        if self.postal_code:
            props['postal_code'] = self.postal_code
        if self.latitude is not None:
            props['latitude'] = self.latitude
        if self.longitude is not None:
            props['longitude'] = self.longitude
        if self.last_payment_date:
            props['last_payment_date'] = self.last_payment_date.isoformat()
        if self.credit_rating:
            props['credit_rating'] = self.credit_rating
        if self.notes:
            props['notes'] = self.notes
        
        return props
    
    def is_payment_overdue(self, days: int = 30) -> bool:
        """Check if payment is overdue."""
        if self.current_balance <= 0:
            return False
        
        if not self.last_payment_date:
            return True
        
        days_since_payment = (datetime.now() - self.last_payment_date).days
        return days_since_payment > days
    
    def get_account_age_years(self) -> int:
        """Get account age in years."""
        delta = datetime.now() - self.account_created_date
        return delta.days // 365
    
    def calculate_usage_tier(self) -> str:
        """
        Classify customer based on consumption.
        Returns: 'low', 'medium', 'high', or 'very_high'
        """
        if self.type == CustomerType.INDUSTRIAL:
            if self.average_monthly_consumption > 100000:
                return "very_high"
            elif self.average_monthly_consumption > 50000:
                return "high"
            elif self.average_monthly_consumption > 10000:
                return "medium"
            else:
                return "low"
        
        elif self.type == CustomerType.COMMERCIAL:
            if self.average_monthly_consumption > 10000:
                return "very_high"
            elif self.average_monthly_consumption > 5000:
                return "high"
            elif self.average_monthly_consumption > 1000:
                return "medium"
            else:
                return "low"
        
        else:  # RESIDENTIAL or MUNICIPAL
            if self.average_monthly_consumption > 100:
                return "very_high"
            elif self.average_monthly_consumption > 50:
                return "high"
            elif self.average_monthly_consumption > 20:
                return "medium"
            else:
                return "low"
    
    def is_vip_customer(self) -> bool:
        """Determine if customer is VIP (long-term, high-value, good payment history)."""
        account_age = self.get_account_age_years()
        usage_tier = self.calculate_usage_tier()
        good_payment = not self.is_payment_overdue(days=30)
        
        return (
            account_age >= 5 and
            usage_tier in ["high", "very_high"] and
            good_payment and
            self.status == CustomerStatus.ACTIVE
        )
