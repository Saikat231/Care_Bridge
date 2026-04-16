# Admin Doctor Management Guide

## Admin Credentials
- **Username:** admin
- **Password:** Admin@123
- **Email:** admin@gmail.com

## Features Available to Admins

### 1. Doctor List Page (`/appointments/doctors/`)
When logged in as admin, you will see extra buttons for each doctor:
- **Edit doctor** - Modify doctor's name and email
- **Delete doctor** - Remove doctor from the system

### 2. Hospital Detail Page (`/hospitals/<id>/`)
When viewing a hospital's doctors, admin users also see:
- **Edit doctor** - Modify doctor's name and email
- **Delete doctor** - Remove doctor from the system

## How to Delete a Doctor

### Step 1: Go to Doctors List
- Navigate to: `http://localhost:8000/appointments/doctors/`
- Or click "Doctors" in the navigation menu

### Step 2: Find the Doctor
- Search by name, specialization, or browse the list
- You will see the doctor cards with action buttons

### Step 3: Click "Delete doctor" Button
- Click the red "Delete doctor" button for the doctor you want to remove
- This will take you to a confirmation page

### Step 4: Confirm Deletion
- Review the doctor's information
- Click "Delete doctor" to confirm (this cannot be undone)
- Or click "Cancel" to abort the operation

### Step 5: Confirmation
- You will be redirected to the doctors list
- A success message will appear: "Doctor deleted successfully."

## Current Demo Doctors

Available doctors to manage:
- **Israfil Islam** (Pediatrics) - Israfil@gmail.com
- **Saikat Khan** (Cardiology) - Saikat@gmail.com
- **Jubu Ahmed** (Orthopedics) - Jubu@gmail.com
- **Sanim Hassan** (Dermatology) - Sanim@gmail.com
- **Rifat Roy** (Neurology) - Rifat@gmail.com
- **Maruf Ali** (Gynecology) - Maruf@gmail.com
- **Khalil Mahmud** (Oncology) - Khalil@gmail.com

## Other Admin Functions

### Edit Doctor Profile
1. Click "Edit doctor" button on any doctor
2. Modify first name, last name, or email
3. Click "Save changes"

### View All Doctors
- Admin can view all available doctors across all hospitals
- Search by name or specialization

### Hospital-Specific Management
- Visit individual hospital pages to manage hospital-specific doctors
- Same edit/delete options available on hospital detail pages
