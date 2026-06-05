# New Features API Documentation

This document describes the 5 new features added to your Django e-commerce project.

---

## 1. 📦 Delivery/Shipping System (`/api/delivery/`)

### Overview
Complete delivery and tracking system with multiple shipping methods and real-time order tracking.

### Endpoints

#### Get Available Shipping Methods
```
GET /api/delivery/shipping-methods/
```
Returns list of all active shipping methods with pricing and delivery times.

**Response:**
```json
{
  "id": 1,
  "name": "Standard Shipping",
  "description": "Regular delivery",
  "price": "5.00",
  "delivery_days": 5,
  "is_active": true
}
```

#### Track Order Delivery
```
GET /api/delivery/tracking/retrieve/{order_id}/
```
Get tracking information for a specific order.

**Response:**
```json
{
  "id": 1,
  "order": 1,
  "shipping_method": {
    "id": 1,
    "name": "Express Shipping",
    "price": "15.00",
    "delivery_days": 2
  },
  "status": "in_transit",
  "tracking_number": "TRK123456789",
  "current_location": "Distribution Center - City",
  "shipped_date": "2024-01-10T10:00:00Z",
  "estimated_delivery": "2024-01-12T18:00:00Z",
  "delivered_date": null,
  "notes": "Package on the way"
}
```

#### View User's Order Tracking
```
GET /api/delivery/tracking/my_orders/
```
Get tracking for all user's orders (authenticated users only).

---

## 2. 🏢 Company/About Section (`/api/company/`)

### Overview
Company information, team members, and social links management.

### Endpoints

#### Get Company Information
```
GET /api/company/info/main/
```
Get main company profile with team members.

**Response:**
```json
{
  "id": 1,
  "name": "Your Company",
  "description": "Company description here",
  "mission": "Our mission",
  "vision": "Our vision",
  "established_year": 2020,
  "email": "contact@company.com",
  "phone": "+998901234567",
  "address": "123 Main Street",
  "city": "Tashkent",
  "country": "Uzbekistan",
  "website": "https://company.com",
  "facebook": "https://facebook.com/company",
  "instagram": "https://instagram.com/company",
  "twitter": "https://twitter.com/company",
  "linkedin": "https://linkedin.com/company/company",
  "logo": "/media/company/logo.png",
  "cover_image": "/media/company/cover.png",
  "team_members": [
    {
      "id": 1,
      "name": "John Doe",
      "position": "ceo",
      "bio": "CEO and founder",
      "email": "john@company.com",
      "profile_image": "/media/team/john.png",
      "linkedin": "https://linkedin.com/in/john",
      "twitter": "https://twitter.com/john",
      "instagram": "https://instagram.com/john"
    }
  ]
}
```

#### Get Team Members
```
GET /api/company/team/
```
Get all active team members.

#### Filter Team by Position
```
GET /api/company/team/by_position/?position=ceo
```
Filter team members by position (ceo, cto, manager, developer, designer, marketing, support, other).

---

## 3. 🔄 Return Order System (`/api/orders/returns/`)

### Overview
Simple return request management system for customers.

### Endpoints

#### Create Return Request
```
POST /api/orders/returns/
```
Create a new return request for an order item.

**Request:**
```json
{
  "order": 1,
  "order_item": 1,
  "reason": "defective",
  "description": "Product stopped working after 2 days"
}
```

**Response Status:** 201 Created

#### Get User's Return Requests
```
GET /api/orders/returns/my_returns/
```
Get all return requests created by current user.

#### View Return Request Details
```
GET /api/orders/returns/{id}/
```
Get specific return request details.

**Response:**
```json
{
  "id": 1,
  "order": 1,
  "order_id": 1,
  "order_item": 1,
  "product_name": "Product Name",
  "reason": "defective",
  "description": "Product stopped working",
  "status": "pending",
  "admin_notes": "",
  "return_shipping_cost": null,
  "refund_amount": null,
  "requested_at": "2024-01-10T10:00:00Z",
  "approved_at": null,
  "received_at": null,
  "completed_at": null
}
```

#### Approve Return Request (Admin)
```
POST /api/orders/returns/{id}/approve/
```
Admin approves a return request.

**Request:**
```json
{
  "notes": "Return approved. Please send item back."
}
```

#### Reject Return Request (Admin)
```
POST /api/orders/returns/{id}/reject/
```
Admin rejects a return request.

**Return Reasons:**
- `defective` - Defective Product
- `damaged` - Damaged in Shipping
- `wrong_item` - Wrong Item Received
- `not_as_described` - Not as Described
- `changed_mind` - Changed Mind
- `other` - Other

---

## 4. 💬 Feedback/Suggestions (`/api/feedback/`)

### Overview
Collect user feedback, suggestions, and complaints about the company.

### Endpoints

#### Create Feedback (No Auth Required)
```
POST /api/feedback/
```
Submit feedback without authentication.

**Request:**
```json
{
  "category": "suggestion",
  "rating": 4,
  "title": "Great service",
  "message": "I really enjoyed your service",
  "name": "John",
  "email": "john@example.com",
  "phone": "+998901234567"
}
```

#### Create Feedback (Authenticated)
```
POST /api/feedback/
```
Submit feedback as authenticated user.

**Request:**
```json
{
  "category": "complaint",
  "rating": 2,
  "title": "Slow delivery",
  "message": "Took too long to deliver"
}
```

#### Get User's Feedback
```
GET /api/feedback/my_feedback/
```
Get authenticated user's feedback (authenticated only).

#### Get Feedback Statistics
```
GET /api/feedback/stats/
```
Get feedback statistics and average rating.

**Response:**
```json
{
  "total_feedback": 150,
  "by_category": {
    "suggestion": 45,
    "complaint": 30,
    "appreciation": 50,
    "bug_report": 15,
    "feature_request": 10,
    "other": 0
  },
  "average_rating": 3.8
}
```

**Feedback Categories:**
- `suggestion` - Suggestion
- `complaint` - Complaint
- `appreciation` - Appreciation
- `bug_report` - Bug Report
- `feature_request` - Feature Request
- `other` - Other

**Ratings:**
- 1 - Very Poor
- 2 - Poor
- 3 - Average
- 4 - Good
- 5 - Excellent

---

## 5. 📧 Contact/Messaging System (`/api/contact/`)

### Overview
Full messaging system with conversation tracking and admin support.

### Endpoints

#### Send Contact Message (No Auth Required)
```
POST /api/contact/
```
Send a contact message without authentication.

**Request:**
```json
{
  "subject": "Product inquiry",
  "message": "I have a question about your products",
  "sender_name": "John Doe",
  "sender_email": "john@example.com",
  "sender_phone": "+998901234567"
}
```

#### Send Contact Message (Authenticated)
```
POST /api/contact/
```
Send a message as authenticated user.

**Request:**
```json
{
  "subject": "Order issue",
  "message": "I have an issue with my order"
}
```

#### Get User's Messages
```
GET /api/contact/my_messages/
```
Get authenticated user's contact messages.

#### Get Message Details
```
GET /api/contact/{id}/
```
Get specific message with conversation history.

**Response:**
```json
{
  "id": 1,
  "subject": "Order issue",
  "message": "I haven't received my order yet",
  "sender_name": "John Doe",
  "sender_email": "john@example.com",
  "sender_phone": "+998901234567",
  "status": "open",
  "priority": "high",
  "assigned_to": 5,
  "replies": [
    {
      "id": 1,
      "sender": 5,
      "sender_name": "Support",
      "content": "We are investigating this issue",
      "is_internal": false,
      "attachments": [],
      "created_at": "2024-01-10T12:00:00Z"
    }
  ],
  "created_at": "2024-01-10T10:00:00Z",
  "updated_at": "2024-01-10T12:00:00Z",
  "resolved_at": null
}
```

#### Add Reply to Message (Admin Only)
```
POST /api/contact/{id}/add_reply/
```
Admin adds a reply to a contact message.

**Request:**
```json
{
  "content": "Thank you for contacting us. We are looking into this.",
  "is_internal": false,
  "attachments": []
}
```

#### Change Message Status (Admin Only)
```
POST /api/contact/{id}/change_status/
```
Admin changes message status.

**Request:**
```json
{
  "status": "in_progress"
}
```

**Status Options:**
- `new` - New
- `open` - Open
- `in_progress` - In Progress
- `resolved` - Resolved
- `closed` - Closed

#### Assign Message (Admin Only)
```
POST /api/contact/{id}/assign_to/
```
Admin assigns message to staff member.

**Request:**
```json
{
  "assigned_to": 5
}
```

#### Get All Messages (Admin Only)
```
GET /api/contact/admin_list/
```
Admin gets all contact messages with optional filters.

**Query Parameters:**
- `status=open` - Filter by status
- `priority=high` - Filter by priority

**Priority Options:**
- `low` - Low
- `medium` - Medium
- `high` - High
- `urgent` - Urgent

---

## Admin Panel Features

All new features have full Django admin integration:

- **Company Info**: `/admin/company/companyinfo/`
  - Add/edit company details
  - Manage team members
  - Upload logo and cover images

- **Delivery**: `/admin/delivery/`
  - Manage shipping methods
  - Track orders
  - Update delivery status

- **Feedback**: `/admin/feedback/feedback/`
  - View all feedback
  - Mark as read/resolved
  - Add admin responses

- **Contact**: `/admin/contact/`
  - Manage contact messages
  - Add replies and internal notes
  - Assign to staff
  - Track resolution status

- **Return Requests**: `/admin/order/returnrequest/`
  - Review return requests
  - Approve/reject returns
  - Set refund amounts
  - Track return status

---

## Authentication Requirements

| Feature | Create | List | Detail | Admin |
|---------|--------|------|--------|-------|
| Delivery | No | No | Auth | No |
| Company | No | No | No | No |
| Feedback | No | Auth* | Auth | Admin |
| Contact | No | Auth* | Auth | Admin |
| Returns | Auth | Auth | Auth | Admin |

*No auth required for creation, but auth required for listing own items

---

## Usage Examples

### Example: Complete Order with Return Flow

1. **User places order** (existing flow)
2. **Track order**: `GET /api/delivery/tracking/my_orders/`
3. **Receive order** - status changes to `delivered`
4. **Request return**: `POST /api/orders/returns/` with reason
5. **Admin reviews** at `/admin/order/returnrequest/`
6. **Admin approves** return
7. **Process refund** - set refund amount and mark completed

### Example: Customer Support Flow

1. **Customer sends message**: `POST /api/contact/` (no auth)
2. **System receives message** - status: `new`
3. **Admin views**: `GET /api/contact/admin_list/?status=new`
4. **Admin assigns**: `POST /api/contact/{id}/assign_to/`
5. **Status updated**: `in_progress`
6. **Admin adds reply**: `POST /api/contact/{id}/add_reply/`
7. **Customer views reply**: `GET /api/contact/{id}/`
8. **Mark resolved**: `POST /api/contact/{id}/change_status/` with `resolved`

---

## Error Handling

All endpoints return standard HTTP status codes:

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `500` - Server Error

---

## Notes

- All image uploads use media directory: `/media/`
- Foreign key relationships are automatically validated
- Timestamps are in ISO 8601 format (UTC)
- Pagination available on list endpoints
- Filtering available on admin endpoints
- Soft delete not implemented (use status for deactivation instead)

---

## Database Migrations

All migrations have been created and applied:

```bash
python manage.py makemigrations
python manage.py migrate
```

---

For questions or issues, contact the development team.
