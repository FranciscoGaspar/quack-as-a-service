#!/usr/bin/env python3
"""
QR Code Generator for Users

This script generates QR codes for users and saves them as image files.

Usage:
    python generate_user_qr_codes.py                    # Generate for all users
    python generate_user_qr_codes.py --user-id 1       # Generate for specific user
    python generate_user_qr_codes.py --create-user "John Doe"  # Create user + QR code
    python generate_user_qr_codes.py --batch-create users.txt  # Batch create from file
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import datetime
import uuid

# Add the backend directory to the path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

try:
    import qrcode
    from PIL import Image
    print("✅ QR code libraries loaded")
except ImportError as e:
    print(f"❌ Missing QR code libraries: {e}")
    print("💡 Install with: pip install qrcode[pil]")
    sys.exit(1)

try:
    from database.services import UserService
    print("✅ Database services loaded")
except ImportError as e:
    print(f"❌ Failed to import database services: {e}")
    sys.exit(1)

class QRCodeGenerator:
    """QR Code generator for users."""
    
    def __init__(self, output_dir="qr_codes"):
        """Initialize QR code generator."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        print(f"📁 QR codes will be saved to: {self.output_dir.absolute()}")
    
    def generate_qr_code_data(self, user):
        """Generate QR code data for a user."""
        if user.qr_code:
            return user.qr_code
        
        # Generate QR code based on user info
        # Format: user_{clean_name}_{id}_{timestamp}
        clean_name = user.name.lower().replace(" ", "_").replace("-", "_")
        clean_name = ''.join(c for c in clean_name if c.isalnum() or c == '_')
        timestamp = datetime.now().strftime("%Y%m")
        qr_data = f"user_{clean_name}_{user.id}_{timestamp}"
        
        return qr_data
    
    def create_qr_image(self, data, size=10, border=4):
        """Create QR code image from data."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=size,
            border=border,
        )
        
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create image with high contrast
        img = qr.make_image(fill_color="black", back_color="white")
        # Convert to RGB mode to avoid palette issues
        if img.mode != 'RGB':
            img = img.convert('RGB')
        return img
    
    def generate_qr_for_user(self, user, update_db=True):
        """Generate QR code for a specific user."""
        print(f"\n👤 Processing user: {user.name} (ID: {user.id})")
        
        # Generate QR data
        qr_data = self.generate_qr_code_data(user)
        print(f"📱 QR Code data: {qr_data}")
        
        # Update user in database if needed
        if update_db and user.qr_code != qr_data:
            try:
                UserService.update(user.id, qr_code=qr_data)
                print(f"✅ Updated user QR code in database")
            except Exception as e:
                print(f"⚠️  Failed to update user QR code: {e}")
        
        # Generate QR code image
        img = self.create_qr_image(qr_data)
        
        # Save image
        filename = f"user_{user.id}_{user.name.replace(' ', '_')}_qr.png"
        filepath = self.output_dir / filename
        
        img.save(filepath)
        print(f"💾 QR code saved: {filepath}")
        
        # Create labeled version
        labeled_filepath = self.create_labeled_qr(img, user, qr_data)
        
        return {
            'user_id': user.id,
            'user_name': user.name,
            'qr_data': qr_data,
            'qr_file': str(filepath),
            'labeled_file': str(labeled_filepath),
            'success': True
        }
    
    def create_labeled_qr(self, qr_img, user, qr_data):
        """Create a labeled QR code with user information."""
        from PIL import Image, ImageDraw, ImageFont
        
        # Create larger canvas for labels
        qr_width, qr_height = qr_img.size
        canvas_width = qr_width + 40
        canvas_height = qr_height + 120
        
        canvas = Image.new('RGB', (canvas_width, canvas_height), 'white')
        
        # Paste QR code centered
        qr_x = (canvas_width - qr_width) // 2
        qr_y = 60
        canvas.paste(qr_img, (qr_x, qr_y, qr_x + qr_width, qr_y + qr_height))
        
        # Add text labels
        draw = ImageDraw.Draw(canvas)
        
        try:
            # Try to use a nice font
            title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
            text_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
        except:
            # Fallback to default font
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
        
        # Title
        title_text = f"Factory ID Badge"
        try:
            title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
        except:
            title_width = len(title_text) * 10  # Fallback calculation
        title_x = (canvas_width - title_width) // 2
        draw.text((title_x, 20), title_text, fill='black', font=title_font)
        
        # User name
        name_text = user.name
        try:
            name_bbox = draw.textbbox((0, 0), name_text, font=text_font)
            name_width = name_bbox[2] - name_bbox[0]
        except:
            name_width = len(name_text) * 8  # Fallback calculation
        name_x = (canvas_width - name_width) // 2
        draw.text((name_x, qr_y + qr_height + 10), name_text, fill='black', font=text_font)
        
        # QR code data (small)
        data_text = f"ID: {qr_data[:30]}..." if len(qr_data) > 30 else f"ID: {qr_data}"
        try:
            data_bbox = draw.textbbox((0, 0), data_text, font=text_font)
            data_width = data_bbox[2] - data_bbox[0]
        except:
            data_width = len(data_text) * 6  # Fallback calculation
        data_x = (canvas_width - data_width) // 2
        draw.text((data_x, qr_y + qr_height + 30), data_text, fill='gray', font=text_font)
        
        # Instructions
        instr_text = "Scan for factory entry"
        try:
            instr_bbox = draw.textbbox((0, 0), instr_text, font=text_font)
            instr_width = instr_bbox[2] - instr_bbox[0]
        except:
            instr_width = len(instr_text) * 6  # Fallback calculation
        instr_x = (canvas_width - instr_width) // 2
        draw.text((instr_x, qr_y + qr_height + 50), instr_text, fill='gray', font=text_font)
        
        # Save labeled version
        filename = f"user_{user.id}_{user.name.replace(' ', '_')}_badge.png"
        filepath = self.output_dir / filename
        canvas.save(filepath)
        print(f"🏷️  Labeled badge saved: {filepath}")
        
        return filepath
    
    def generate_for_all_users(self):
        """Generate QR codes for all users."""
        users = UserService.get_all()
        
        if not users:
            print("⚠️  No users found in database")
            return []
        
        print(f"👥 Found {len(users)} users")
        results = []
        
        for user in users:
            try:
                result = self.generate_qr_for_user(user)
                results.append(result)
            except Exception as e:
                print(f"❌ Failed to generate QR for user {user.name}: {e}")
                results.append({
                    'user_id': user.id,
                    'user_name': user.name,
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def create_user_with_qr(self, name):
        """Create a new user and generate QR code."""
        print(f"👤 Creating new user: {name}")
        
        try:
            # Generate QR data first
            clean_name = name.lower().replace(" ", "_").replace("-", "_")
            clean_name = ''.join(c for c in clean_name if c.isalnum() or c == '_')
            timestamp = datetime.now().strftime("%Y%m")
            # Create unique ID using timestamp and random component
            unique_id = str(uuid.uuid4().hex[:8])
            qr_data = f"user_{clean_name}_{unique_id}_{timestamp}"
            
            # Create user
            user = UserService.create(name=name, qr_code=qr_data)
            print(f"✅ Created user: {user.name} (ID: {user.id})")
            
            # Generate QR code
            result = self.generate_qr_for_user(user, update_db=False)
            return result
            
        except Exception as e:
            print(f"❌ Failed to create user {name}: {e}")
            return {
                'user_name': name,
                'success': False,
                'error': str(e)
            }
    
    def batch_create_users(self, filename):
        """Create multiple users from a text file."""
        filepath = Path(filename)
        
        if not filepath.exists():
            print(f"❌ File not found: {filename}")
            return []
        
        print(f"📄 Reading users from: {filename}")
        
        results = []
        with open(filepath, 'r') as f:
            for line_num, line in enumerate(f, 1):
                name = line.strip()
                if not name or name.startswith('#'):
                    continue
                
                print(f"\n📝 Line {line_num}: {name}")
                result = self.create_user_with_qr(name)
                results.append(result)
        
        return results

def create_sample_users_file():
    """Create a sample users.txt file."""
    sample_users = [
        "# Sample users file",
        "# One user name per line",
        "# Lines starting with # are ignored",
        "",
        "John Doe",
        "Jane Smith", 
        "Alice Johnson",
        "Bob Wilson",
        "Carol Davis"
    ]
    
    with open("sample_users.txt", "w") as f:
        f.write("\n".join(sample_users))
    
    print("✅ Created sample_users.txt")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Generate QR codes for users")
    parser.add_argument("--user-id", type=int, help="Generate QR for specific user ID")
    parser.add_argument("--create-user", type=str, help="Create new user with QR code")
    parser.add_argument("--batch-create", type=str, help="Batch create users from text file")
    parser.add_argument("--output-dir", type=str, default="qr_codes", help="Output directory for QR codes")
    parser.add_argument("--sample-file", action="store_true", help="Create sample users.txt file")
    
    args = parser.parse_args()
    
    if args.sample_file:
        create_sample_users_file()
        return
    
    # Initialize generator
    generator = QRCodeGenerator(args.output_dir)
    
    print("🚀 QR Code Generator for Factory Users")
    print("=" * 50)
    
    if args.user_id:
        # Generate for specific user
        user = UserService.get_by_id(args.user_id)
        if not user:
            print(f"❌ User with ID {args.user_id} not found")
            return
        
        result = generator.generate_qr_for_user(user)
        if result['success']:
            print(f"\n🎉 QR code generated successfully!")
            print(f"   QR File: {result['qr_file']}")
            print(f"   Badge File: {result['labeled_file']}")
    
    elif args.create_user:
        # Create new user with QR
        result = generator.create_user_with_qr(args.create_user)
        if result['success']:
            print(f"\n🎉 User created with QR code!")
            print(f"   QR File: {result['qr_file']}")
            print(f"   Badge File: {result['labeled_file']}")
    
    elif args.batch_create:
        # Batch create users
        results = generator.batch_create_users(args.batch_create)
        
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        print(f"\n📊 Batch creation results:")
        print(f"   ✅ Successful: {len(successful)}")
        print(f"   ❌ Failed: {len(failed)}")
        
        if failed:
            print(f"\n❌ Failed users:")
            for result in failed:
                print(f"   - {result['user_name']}: {result.get('error', 'Unknown error')}")
    
    else:
        # Generate for all users
        results = generator.generate_for_all_users()
        
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        print(f"\n📊 Generation complete!")
        print(f"   ✅ Successful: {len(successful)}")
        print(f"   ❌ Failed: {len(failed)}")
        
        if successful:
            print(f"\n✅ Generated QR codes:")
            for result in successful:
                print(f"   📱 {result['user_name']}: {result['qr_data']}")
        
        if failed:
            print(f"\n❌ Failed users:")
            for result in failed:
                print(f"   - {result['user_name']}: {result.get('error', 'Unknown error')}")
    
    print(f"\n💾 All files saved to: {Path(args.output_dir).absolute()}")

if __name__ == "__main__":
    main()
