import streamlit as st
import json
from datetime import datetime, timedelta
from typing import List, Dict
import re
from collections import Counter

st.set_page_config(page_title="VIDeMI Email Sequence Builder", page_icon="📧", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .stat-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    .email-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .template-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        margin-bottom: 1rem;
        cursor: pointer;
        transition: all 0.3s;
    }
    .template-card:hover {
        border-color: #667eea;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Default header and footer images
DEFAULT_HEADER_IMAGE = "https://videmiservices.com/wp-content/uploads/2025/10/PHOTO-2025-10-06-17-20-39.jpg"
DEFAULT_FOOTER_IMAGE = "https://videmiservices.com/wp-content/uploads/2025/10/PHOTO-2025-10-06-17-31-56.jpg"

EMAIL_TEMPLATES = {
    "welcome": {
        "name": "Welcome Email",
        "subject": "Welcome to VIDeMI Services! 🏠",
        "category": "Onboarding",
        "content": '''<h1 style="color: #2c3e50; font-size: 28px; margin-bottom: 20px;">Welcome to VIDeMI Services!</h1>
<p style="color: #555555; font-size: 16px; line-height: 1.6; margin-bottom: 15px;">
    Dear Valued Customer,
</p>
<p style="color: #555555; font-size: 16px; line-height: 1.6; margin-bottom: 15px;">
    Thank you for choosing VIDeMI Services! We're thrilled to have you join our family of satisfied customers who trust us with their cleaning and maintenance needs.
</p>
<p style="color: #555555; font-size: 16px; line-height: 1.6; margin-bottom: 15px;">
    At VIDeMI, we're committed to providing exceptional service that exceeds your expectations. Whether you need regular cleaning, deep cleaning, or specialized services, we're here to help.
</p>
<p style="color: #555555; font-size: 16px; line-height: 1.6; margin-bottom: 20px;">
    Over the next few weeks, we'll be sharing valuable information about our services, tips for maintaining your space, and exclusive offers just for you.
</p>
<p style="color: #555555; font-size: 16px; line-height: 1.6;">
    Best regards,<br>
    <strong>The VIDeMI Services Team</strong>
</p>'''
    },
    "services": {
        "name": "Services Overview",
        "subject": "Discover Our Complete Range of Services",
        "category": "Educational",
        "content": '''<h1 style="color: #2c3e50; font-size: 28px; margin-bottom: 20px;">Discover What We Can Do For You</h1>
<p style="color: #555555; font-size: 16px; line-height: 1.6; margin-bottom: 20px;">
    VIDeMI Services offers a comprehensive range of cleaning and maintenance solutions tailored to your needs:
</p>
<ul style="color: #555555; font-size: 16px; line-height: 1.8; margin-bottom: 20px;">
    <li><strong>Regular Cleaning:</strong> Keep your space consistently clean with our scheduled services</li>
    <li><strong>Deep Cleaning:</strong> Thorough cleaning for those hard-to-reach areas</li>
    <li><strong>Streamlit Cleaning:</strong> Specialized cleaning for modern surfaces and materials</li>
    <li><strong>Move-In/Move-Out:</strong> Complete cleaning for transitions</li>
    <li><strong>Commercial Services:</strong> Professional cleaning for businesses</li>
</ul>
<div style="background-color: #667eea; color: white; padding: 20px; border-radius: 8px; text-align: center; margin-top: 30px;">
    <h3 style="margin: 0 0 10px 0;">Ready to Get Started?</h3>
    <p style="margin: 0 0 15px 0;">Contact us today to schedule your service!</p>
    <a href="#" style="background-color: white; color: #667eea; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">Book Now</a>
</div>'''
    },
    "streamlit": {
        "name": "Streamlit Cleaning Deep Dive",
        "subject": "Introducing Streamlit Cleaning: The Future of Surface Care",
        "category": "Service Spotlight",
        "content": '''<h1 style="color: #2c3e50; font-size: 28px; margin-bottom: 20px;">Streamlit Cleaning: Advanced Surface Care</h1>
<p style="color: #555555; font-size: 16px; line-height: 1.6; margin-bottom: 20px;">
    Our revolutionary Streamlit Cleaning service is designed for modern homes and businesses with contemporary surfaces and materials.
</p>
<div style="background-color: #f8f9fa; padding: 25px; border-radius: 8px; margin-bottom: 25px;">
    <h2 style="color: #2c3e50; font-size: 22px; margin-bottom: 15px;">What is Streamlit Cleaning?</h2>
    <p style="color: #555555; font-size: 16px; line-height: 1.6; margin-bottom: 15px;">
        Streamlit Cleaning uses advanced techniques and specialized products to clean and protect modern surfaces including:
    </p>
    <ul style="color: #555555; font-size: 16px; line-height: 1.8;">
        <li>High-gloss and matte finishes</li>
        <li>Smart home surfaces and touchscreens</li>
        <li>Engineered stone and quartz countertops</li>
        <li>Modern flooring materials</li>
        <li>Stainless steel and chrome fixtures</li>
        <li>Glass and acrylic surfaces</li>
    </ul>
</div>
<div style="background-color: #667eea; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
    <h3 style="margin: 0 0 15px 0; font-size: 20px;">Benefits of Streamlit Cleaning</h3>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
        <div>
            <strong>✓ Streak-Free Results</strong><br>
            <span style="font-size: 14px;">Perfect clarity on all surfaces</span>
        </div>
        <div>
            <strong>✓ Long-Lasting Protection</strong><br>
            <span style="font-size: 14px;">Surfaces stay cleaner longer</span>
        </div>
        <div>
            <strong>✓ Safe for Technology</strong><br>
            <span style="font-size: 14px;">Won't damage sensitive electronics</span>
        </div>
        <div>
            <strong>✓ Eco-Friendly</strong><br>
            <span style="font-size: 14px;">Environmentally responsible products</span>
        </div>
    </div>
</div>
<p style="color: #555555; font-size: 16px; line-height: 1.6; margin-bottom: 15px;">
    <strong>Special Introductory Offer:</strong> Book your first Streamlit Cleaning service and receive 20% off!
</p>
<p style="color: #555555; font-size: 16px; line-height: 1.6;">
    Contact us today to learn more about how Streamlit Cleaning can transform your space.
</p>'''
    },
    "difference": {
        "name": "Why Choose Us",
        "subject": "The VIDeMI Difference: Quality You Can Trust",
        "category": "Brand",
        "content": '''<h1 style="color: #2c3e50; font-size: 28px; margin-bottom: 20px;">Why Choose VIDeMI?</h1>
<p style="color: #555555; font-size: 16px; line-height: 1.6; margin-bottom: 20px;">
    We're not just another cleaning service. Here's what sets us apart:
</p>
<div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
    <h3 style="color: #2c3e50; font-size: 20px; margin-bottom: 15px;">✓ Experienced Professionals</h3>
    <p style="color: #555555; font-size: 16px; line-height: 1.6; margin-bottom: 15px;">
        Our team is trained, vetted, and dedicated to excellence. Every team member undergoes rigorous background checks and continuous training.
    </p>
    
    <h3 style="color: #2c3e50; font-size: 20px; margin-bottom: 15px;">✓ Eco-Friendly Products</h3>
    <p style="color: #555555; font-size: 16px; line-height: 1.6; margin-bottom: 15px;">
        We use environmentally safe cleaning solutions that are tough on dirt but gentle on your home and the planet.
    </p>
    
    <h3 style="color: #2c3e50; font-size: 20px; margin-bottom: 15px;">✓ Satisfaction Guaranteed</h3>
    <p style="color: #555555; font-size: 16px; line-height: 1.6; margin-bottom: 15px;">
        If you're not completely satisfied, we'll make it right. That's our promise to you.
    </p>
    
    <h3 style="color: #2c3e50; font-size: 20px; margin-bottom: 15px;">✓ Flexible Scheduling</h3>
    <p style="color: #555555; font-size: 16px; line-height: 1.6;">
        We work around your schedule with convenient booking options and reliable service.
    </p>
</div>'''
    },
    "tips": {
        "name": "Maintenance Tips",
        "subject": "Pro Tips: Keep Your Space Spotless Between Cleanings",
        "category": "Educational",
        "content": '''<h1 style="color: #2c3e50; font-size: 28px; margin-bottom: 20px;">Professional Maintenance Tips</h1>
<p style="color: #555555; font-size: 16px; line-height: 1.6; margin-bottom: 20px;">
    Want to keep your space looking great between professional cleanings? Here are our top tips:
</p>
<div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 15px;">
    <h3 style="color: #667eea; font-size: 18px; margin-bottom: 10px;">Daily Habits</h3>
    <ul style="color: #555555; font-size: 16px; line-height: 1.8;">
        <li>Make your bed every morning</li>
        <li>Wipe down kitchen counters after use</li>
        <li>Do dishes immediately or load dishwasher</li>
        <li>Quick vacuum high-traffic areas</li>
    </ul>
</div>
<div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 15px;">
    <h3 style="color: #667eea; font-size: 18px; margin-bottom: 10px;">Weekly Tasks</h3>
    <ul style="color: #555555; font-size: 16px; line-height: 1.8;">
        <li>Change bed linens</li>
        <li>Clean bathroom surfaces</li>
        <li>Dust furniture and electronics</li>
        <li>Mop hard floors</li>
    </ul>
</div>
<div style="background-color: #fff3cd; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
    <p style="color: #856404; font-size: 16px; line-height: 1.6; margin: 0;">
        <strong>Pro Tip:</strong> The 10-minute tidy! Set a timer for 10 minutes each evening and do a quick pickup. You'll be amazed at the difference!
    </p>
</div>'''
    },
    "seasonal": {
        "name": "Seasonal Cleaning Guide",
        "subject": "Seasonal Cleaning: Prepare Your Space for the Season",
        "category": "Educational",
        "content": '''<h1 style="color: #2c3e50; font-size: 28px; margin-bottom: 20px;">Seasonal Cleaning Guide</h1>
<p style="color: #555555; font-size: 16px; line-height: 1.6; margin-bottom: 20px;">
    Each season brings unique cleaning challenges and opportunities. Here's your guide to seasonal maintenance:
</p>
<div style="background-color: #e3f2fd; padding: 20px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #2196f3;">
    <h3 style="color: #1976d2; font-size: 20px; margin-bottom: 10px;">Spring Cleaning</h3>
    <p style="color: #555555; font-size: 16px; line-height: 1.6;">
        Deep clean windows, organize closets, clean gutters, and refresh outdoor spaces.
    </p>
</div>
<div style="background-color: #fff9c4; padding: 20px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #fbc02d;">
    <h3 style="color: #f57f17; font-size: 20px; margin-bottom: 10px;">Summer Maintenance</h3>
    <p style="color: #555555; font-size: 16px; line-height: 1.6;">
        Focus on outdoor areas, clean air conditioning units, and maintain high-traffic zones.
    </p>
</div>
<div style="background-color: #ffe0b2; padding: 20px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #ff9800;">
    <h3 style="color: #e65100; font-size: 20px; margin-bottom: 10px;">Fall Preparation</h3>
    <p style="color: #555555; font-size: 16px; line-height: 1.6;">
        Prepare for winter, clean heating systems, organize storage, and weatherproof spaces.
    </p>
</div>
<div style="background-color: #e1f5fe; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #0288d1;">
    <h3 style="color: #01579b; font-size: 20px; margin-bottom: 10px;">Winter Care</h3>
    <p style="color: #555555; font-size: 16px; line-height: 1.6;">
        Combat dry air, prevent mold, maintain indoor air quality, and keep entryways clean.
    </p>
</div>
<p style="color: #555555; font-size: 16px; line-height: 1.6;">
    <strong>Need help with seasonal deep cleaning?</strong> Our team is ready to tackle any seasonal cleaning challenge!
</p>'''
    },
    "testimonial": {
        "name": "Customer Success Story",
        "subject": "See Why Customers Love VIDeMI Services",
        "category": "Social Proof",
        "content": '''<h1 style="color: #2c3e50; font-size: 28px; margin-bottom: 20px;">What Our Customers Say</h1>
<p style="color: #555555; font-size: 16px; line-height: 1.6; margin-bottom: 30px;">
    Don't just take our word for it. Here's what our satisfied customers have to say:
</p>
<div style="background-color: #f8f9fa; padding: 25px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #667eea;">
    <p style="color: #555555; font-size: 16px; line-height: 1.6; font-style: italic; margin-bottom: 15px;">
        "VIDeMI Services transformed our home! Their attention to detail is incredible, and the Streamlit Cleaning service made our modern kitchen look brand new. Highly recommended!"
    </p>
    <p style="color: #667eea; font-weight: bold; margin: 0;">
        - Sarah M., Homeowner
    </p>
</div>
<div style="background-color: #f8f9fa; padding: 25px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #667eea;">
    <p style="color: #555555; font-size: 16px; line-height: 1.6; font-style: italic; margin-bottom: 15px;">
        "As a busy professional, I don't have time for deep cleaning. VIDeMI's team is reliable, thorough, and always goes above and beyond. They're worth every penny!"
    </p>
    <p style="color: #667eea; font-weight: bold; margin: 0;">
        - Michael T., Business Owner
    </p>
</div>
<div style="background-color: #f8f9fa; padding: 25px; border-radius: 8px; margin-bottom: 30px; border-left: 4px solid #667eea;">
    <p style="color: #555555; font-size: 16px; line-height: 1.6; font-style: italic; margin-bottom: 15px;">
        "We've tried several cleaning services, but VIDeMI is by far the best. Their eco-friendly products are perfect for our family, and our home has never looked better!"
    </p>
    <p style="color: #667eea; font-weight: bold; margin: 0;">
        - Jennifer & David L., Family
    </p>
</div>
<div style="text-align: center; background-color: #667eea; color: white; padding: 25px; border-radius: 8px;">
    <h3 style="margin: 0 0 10px 0;">Join Our Happy Customers!</h3>
    <p style="margin: 0 0 20px 0;">Experience the VIDeMI difference for yourself.</p>
    <a href="#" style="background-color: white; color: #667eea; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">Schedule Your Service</a>
</div>'''
    },
    "offer": {
        "name": "Special Offer",
        "subject": "Exclusive Offer: Save 25% on Your Next Service!",
        "category": "Promotional",
        "content": '''<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px;">
    <h1 style="color: white; font-size: 32px; margin-bottom: 15px;">Special Offer Just For You!</h1>
    <p style="color: white; font-size: 20px; margin: 0;">Save 25% on Your Next Service</p>
</div>
<p style="color: #555555; font-size: 16px; line-height: 1.6; margin-bottom: 20px;">
    As a valued customer, we're excited to offer you an exclusive discount on your next cleaning service!
</p>
<div style="background-color: #fff3cd; padding: 25px; border-radius: 8px; margin-bottom: 25px; text-align: center;">
    <h2 style="color: #856404; font-size: 28px; margin-bottom: 10px;">Use Code: VIDEMI25</h2>
    <p style="color: #856404; font-size: 16px; margin: 0;">Valid for the next 14 days</p>
</div>
<div style="background-color: #f8f9fa; padding: 25px; border-radius: 8px; margin-bottom: 25px;">
    <h3 style="color: #2c3e50; font-size: 20px; margin-bottom: 15px;">This Offer Includes:</h3>
    <ul style="color: #555555; font-size: 16px; line-height: 1.8;">
        <li>25% off any regular or deep cleaning service</li>
        <li>Free Streamlit Cleaning upgrade (valued at $50)</li>
        <li>Complimentary eco-friendly product sample kit</li>
        <li>Priority scheduling</li>
    </ul>
</div>
<div style="text-align: center; margin-top: 30px;">
    <a href="#" style="background-color: #667eea; color: white; padding: 15px 40px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 18px; display: inline-block;">Book Now & Save</a>
</div>
<p style="color: #999999; font-size: 14px; text-align: center; margin-top: 20px;">
    *Offer expires in 14 days. Cannot be combined with other offers. New bookings only.
</p>'''
    },
    "loyalty": {
        "name": "Loyalty Program",
        "subject": "Introducing VIDeMI Rewards: Earn Points with Every Service",
        "category": "Promotional",
        "content": '''<h1 style="color: #2c3e50; font-size: 28px; margin-bottom: 20px;">Introducing VIDeMI Rewards</h1>
<p style="color: #555555; font-size: 16px; line-height: 1.6; margin-bottom: 25px;">
    We're excited to announce our new loyalty program designed to reward our valued customers like you!
</p>
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; color: white; margin-bottom: 25px;">
    <h2 style="font-size: 24px; margin-bottom: 20px; text-align: center;">How It Works</h2>
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; text-align: center;">
        <div>
            <div style="font-size: 36px; margin-bottom: 10px;">1️⃣</div>
            <strong>Earn Points</strong><br>
            <span style="font-size: 14px;">Get 1 point per dollar spent</span>
        </div>
        <div>
            <div style="font-size: 36px; margin-bottom: 10px;">2️⃣</div>
            <strong>Accumulate</strong><br>
            <span style="font-size: 14px;">Watch your points grow</span>
        </div>
        <div>
            <div style="font-size: 36px; margin-bottom: 10px;">3️⃣</div>
            <strong>Redeem</strong><br>
            <span style="font-size: 14px;">Use points for discounts</span>
        </div>
    </div>
</div>
<div style="background-color: #f8f9fa; padding: 25px; border-radius: 8px; margin-bottom: 25px;">
    <h3 style="color: #2c3e50; font-size: 20px; margin-bottom: 15px;">Reward Tiers</h3>
    <div style="margin-bottom: 15px; padding: 15px; background-color: #e8eaf6; border-radius: 5px;">
        <strong style="color: #667eea;">Silver (0-500 points):</strong> 5% off future services
    </div>
    <div style="margin-bottom: 15px; padding: 15px; background-color: #ffd700; border-radius: 5px;">
        <strong style="color: #856404;">Gold (501-1000 points):</strong> 10% off + priority scheduling
    </div>
    <div style="padding: 15px; background-color: #e0e0e0; border-radius: 5px;">
        <strong style="color: #424242;">Platinum (1001+ points):</strong> 15% off + free upgrades + exclusive perks
    </div>
</div>
<div style="background-color: #d4edda; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
    <p style="color: #155724; font-size: 16px; line-height: 1.6; margin: 0;">
        <strong>Good News!</strong> You've been automatically enrolled and already have points from your previous services!
    </p>
</div>
<p style="color: #555555; font-size: 16px; line-height: 1.6; text-align: center;">
    Log in to your account to check your points balance and start redeeming rewards today!
</p>'''
    },
    "referral": {
        "name": "Referral Program",
        "subject": "Refer a Friend, Get $50 Credit!",
        "category": "Promotional",
        "content": '''<h1 style="color: #2c3e50; font-size: 28px; margin-bottom: 20px;">Share the Love, Earn Rewards!</h1>
<p style="color: #555555; font-size: 16px; line-height: 1.6; margin-bottom: 25px;">
    Love VIDeMI Services? Share the experience with friends and family and earn rewards for every referral!
</p>
<div style="background-color: #667eea; color: white; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 25px;">
    <h2 style="font-size: 32px; margin-bottom: 10px;">$50 Credit</h2>
    <p style="font-size: 18px; margin: 0;">For Every Friend Who Books a Service</p>
</div>
<div style="background-color: #f8f9fa; padding: 25px; border-radius: 8px; margin-bottom: 25px;">
    <h3 style="color: #2c3e50; font-size: 20px; margin-bottom: 15px;">How It Works:</h3>
    <ol style="color: #555555; font-size: 16px; line-height: 2;">
        <li>Share your unique referral code with friends</li>
        <li>They book their first service using your code</li>
        <li>They get 20% off their first service</li>
        <li>You get $50 credit toward your next service</li>
    </ol>
</div>
<div style="background-color: #fff3cd; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 25px;">
    <h3 style="color: #856404; font-size: 20px; margin-bottom: 10px;">Your Referral Code</h3>
    <div style="background-color: white; padding: 15px; border-radius: 5px; font-size: 24px; font-weight: bold; color: #667eea; letter-spacing: 2px;">
        VIDEMI-FRIEND
    </div>
</div>
<p style="color: #555555; font-size: 16px; line-height: 1.6; margin-bottom: 15px;">
    <strong>No Limit!</strong> Refer as many friends as you want. The more you share, the more you save!
</p>
<div style="text-align: center; margin-top: 30px;">
    <a href="#" style="background-color: #667eea; color: white; padding: 15px 40px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 18px; display: inline-block;">Share Your Code</a>
</div>'''
    },
    "feedback": {
        "name": "Feedback Request",
        "subject": "We'd Love Your Feedback!",
        "category": "Engagement",
        "content": '''<h1 style="color: #2c3e50; font-size: 28px; margin-bottom: 20px;">Your Opinion Matters!</h1>
<p style="color: #555555; font-size: 16px; line-height: 1.6; margin-bottom: 25px;">
    We hope you're enjoying VIDeMI Services! Your feedback helps us improve and serve you better.
</p>
<div style="background-color: #f8f9fa; padding: 25px; border-radius: 8px; margin-bottom: 25px; text-align: center;">
    <h2 style="color: #2c3e50; font-size: 22px; margin-bottom: 20px;">How would you rate your experience?</h2>
    <div style="font-size: 40px; margin-bottom: 15px;">
        ⭐ ⭐ ⭐ ⭐ ⭐
    </div>
    <a href="#" style="background-color: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block; margin-top: 10px;">Leave a Review</a>
</div>
<div style="background-color: #e3f2fd; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
    <h3 style="color: #1976d2; font-size: 18px; margin-bottom: 15px;">Quick Survey (2 minutes)</h3>
    <p style="color: #555555; font-size: 16px; line-height: 1.6; margin-bottom: 15px;">
        Help us understand what we're doing well and where we can improve:
    </p>
    <ul style="color: #555555; font-size: 16px; line-height: 1.8;">
        <li>Quality of service</li>
        <li>Professionalism of staff</li>
        <li>Value for money</li>
        <li>Likelihood to recommend</li>
    </ul>
    <a href="#" style="background-color: #1976d2; color: white; padding: 10px 25px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block; margin-top: 10px;">Take Survey</a>
</div>
<div style="background-color: #d4edda; padding: 20px; border-radius: 8px;">
    <p style="color: #155724; font-size: 16px; line-height: 1.6; margin: 0;">
        <strong>Thank You Bonus:</strong> Complete the survey and receive 100 loyalty points!
    </p>
</div>'''
    }
}

def analyze_email_content(content: str) -> Dict:
    """Analyze email content and return statistics"""
    # Remove HTML tags for text analysis
    text = re.sub(r'<[^>]+>', '', content)
    
    words = text.split()
    word_count = len(words)
    char_count = len(text)
    
    # Count links
    links = re.findall(r'href="[^"]*"', content)
    link_count = len(links)
    
    # Count images
    images = re.findall(r'<img[^>]*>', content)
    image_count = len(images)
    
    # Estimate reading time (average 200 words per minute)
    reading_time = max(1, round(word_count / 200))
    
    return {
        "word_count": word_count,
        "char_count": char_count,
        "link_count": link_count,
        "image_count": image_count,
        "reading_time": reading_time
    }

def validate_email(email: Dict) -> List[str]:
    """Validate email and return list of warnings"""
    warnings = []
    
    if not email.get('subject'):
        warnings.append("Missing subject line")
    elif len(email['subject']) > 100:
        warnings.append("Subject line is too long (>100 characters)")
    elif len(email['subject']) < 10:
        warnings.append("Subject line is too short (<10 characters)")
    
    if not email.get('email_body'):
        warnings.append("Missing email body")
    else:
        stats = analyze_email_content(email['email_body'])
        if stats['word_count'] < 50:
            warnings.append("Email content is very short (<50 words)")
        if stats['word_count'] > 1000:
            warnings.append("Email content is very long (>1000 words)")
    
    if email.get('delay', 0) < 0:
        warnings.append("Delay cannot be negative")
    
    return warnings

def calculate_send_dates(sequence: List[Dict], start_date: datetime = None) -> List[Dict]:
    """Calculate when each email will be sent"""
    if start_date is None:
        start_date = datetime.now()
    
    schedule = []
    for email in sequence:
        send_date = start_date + timedelta(days=email.get('delay', 0))
        schedule.append({
            "email_id": email.get('id'),
            "subject": email.get('subject'),
            "send_date": send_date.strftime("%Y-%m-%d"),
            "days_from_start": email.get('delay', 0)
        })
    
    return schedule

def create_email_html_template(content: str, header_img: str, footer_img: str) -> str:
    """Create a properly formatted HTML email template"""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VIDeMI Services</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f4f4f4;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td align="center" style="padding: 0;">
                <table role="presentation" style="width: 600px; border-collapse: collapse; background-color: #ffffff; margin: 20px auto;">
                    <tr>
                        <td style="padding: 0;">
                            <div class="header-image">
                                <img src="{header_img}" alt="VIDeMI Services Header" style="width: 100%; height: auto; display: block; border: 0;">
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 40px 30px;">
                            {content}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 0;">
                            <div class="footer-image">
                                <img src="{footer_img}" alt="VIDeMI Services Footer" style="width: 100%; height: auto; display: block; border: 0;">
                            </div>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>'''

def create_email_sequence(num_emails: int, start_id: int = 1) -> List[Dict]:
    """Create a complete email sequence"""
    sequence = []
    
    template_keys = list(EMAIL_TEMPLATES.keys())
    
    for i in range(num_emails):
        email_num = i + 1
        
        # Use template if available, otherwise create generic content
        if i < len(template_keys):
            template = EMAIL_TEMPLATES[template_keys[i]]
            subject = template['subject']
            content = template['content']
        else:
            subject = f"VIDeMI Services - Email {email_num}"
            content = f'''<h1 style="color: #2c3e50; font-size: 28px; margin-bottom: 20px;">Email {email_num} of {num_emails}</h1>
<p style="color: #555555; font-size: 16px; line-height: 1.6; margin-bottom: 15px;">
    This is email {email_num} in your welcome sequence.
</p>
<p style="color: #555555; font-size: 16px; line-height: 1.6;">
    Edit this content to customize your message.
</p>'''
        
        # Calculate delay (in days)
        if email_num == 1:
            delay = 0
        elif email_num <= 5:
            delay = email_num - 1
        elif email_num <= 10:
            delay = (email_num - 1) * 2
        elif email_num <= 21:
            delay = (email_num - 1) * 3
        else:
            delay = (email_num - 1) * 7  # Weekly for 52-email sequences
        
        email = {
            "id": start_id + i,
            "subject": subject,
            "email_body": create_email_html_template(
                content,
                DEFAULT_HEADER_IMAGE,
                DEFAULT_FOOTER_IMAGE
            ),
            "delay": delay,
            "status": "active"
        }
        sequence.append(email)
    
    return sequence

st.markdown('<div class="main-header"><h1 style="margin:0;">📧 VIDeMI Email Sequence Builder</h1><p style="margin:10px 0 0 0; opacity:0.9;">Create, edit, and manage professional email sequences</p></div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    st.subheader("Image URLs")
    header_img = st.text_input("Header Image", value=DEFAULT_HEADER_IMAGE, help="URL for email header image")
    footer_img = st.text_input("Footer Image", value=DEFAULT_FOOTER_IMAGE, help="URL for email footer image")
    
    st.divider()
    
    st.subheader("📊 Quick Stats")
    if 'sequence' in st.session_state and st.session_state.sequence:
        seq = st.session_state.sequence
        st.metric("Total Emails", len(seq))
        st.metric("Active Emails", sum(1 for e in seq if e.get('status') == 'active'))
        total_days = max([e.get('delay', 0) for e in seq]) if seq else 0
        st.metric("Sequence Duration", f"{total_days} days")
    else:
        st.info("No sequence loaded")
    
    st.divider()
    
    st.subheader("💾 Export Options")
    if 'sequence' in st.session_state and st.session_state.sequence:
        export_format = st.selectbox("Format", ["JSON (Pretty)", "JSON (Compact)", "CSV Summary"])
        
        if export_format == "CSV Summary":
            import io
            csv_buffer = io.StringIO()
            csv_buffer.write("ID,Subject,Delay (days),Status,Word Count\n")
            for email in st.session_state.sequence:
                stats = analyze_email_content(email.get('email_body', ''))
                csv_buffer.write(f"{email.get('id')},{email.get('subject')},{email.get('delay')},{email.get('status')},{stats['word_count']}\n")
            
            st.download_button(
                label="📥 Download CSV",
                data=csv_buffer.getvalue(),
                file_name="email_sequence_summary.csv",
                mime="text/csv"
            )

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Create/Edit", "📚 Templates", "📊 Analytics", "📅 Schedule", "⚙️ Advanced"])

with tab1:
    st.header("Create or Edit Email Sequence")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Sequence Settings")
        
        mode = st.radio("Mode", ["Create New", "Load Existing"], horizontal=True)
        
        if mode == "Create New":
            num_emails = st.selectbox(
                "Number of Emails",
                options=[3, 5, 10, 21, 52],
                index=2,
                help="Choose how many emails in your sequence"
            )
            
            start_id = st.number_input("Starting ID", min_value=1, value=1, step=1)
            
            if st.button("🚀 Generate Sequence", type="primary", use_container_width=True):
                st.session_state.sequence = create_email_sequence(num_emails, start_id)
                st.success(f"✅ Generated {num_emails} email sequence!")
                st.rerun()
        
        else:  # Load Existing
            uploaded_file = st.file_uploader("Upload JSON file", type=['json'])
            
            if uploaded_file is not None:
                try:
                    sequence = json.load(uploaded_file)
                    st.session_state.sequence = sequence
                    st.success(f"✅ Loaded {len(sequence)} emails!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error loading file: {str(e)}")
    
    with col2:
        st.subheader("Quick Actions")
        
        if 'sequence' in st.session_state and st.session_state.sequence:
            if st.button("➕ Add Email", use_container_width=True):
                new_id = max([e.get('id', 0) for e in st.session_state.sequence]) + 1
                new_email = {
                    "id": new_id,
                    "subject": f"New Email {new_id}",
                    "email_body": create_email_html_template(
                        "<h1>New Email</h1><p>Edit this content...</p>",
                        header_img,
                        footer_img
                    ),
                    "delay": 0,
                    "status": "active"
                }
                st.session_state.sequence.append(new_email)
                st.success("✅ Added new email!")
                st.rerun()
            
            if st.button("🔄 Duplicate Selected", use_container_width=True):
                if 'selected_email_idx' in st.session_state:
                    idx = st.session_state.selected_email_idx
                    original = st.session_state.sequence[idx].copy()
                    new_id = max([e.get('id', 0) for e in st.session_state.sequence]) + 1
                    original['id'] = new_id
                    original['subject'] = f"{original['subject']} (Copy)"
                    st.session_state.sequence.append(original)
                    st.success("✅ Duplicated email!")
                    st.rerun()
            
            if st.button("🗑️ Delete Selected", use_container_width=True):
                if 'selected_email_idx' in st.session_state and len(st.session_state.sequence) > 1:
                    idx = st.session_state.selected_email_idx
                    del st.session_state.sequence[idx]
                    st.success("✅ Deleted email!")
                    st.rerun()
                else:
                    st.warning("Cannot delete the last email!")
        else:
            st.info("Create or load a sequence to see quick actions")
    
    if 'sequence' in st.session_state and st.session_state.sequence:
        st.divider()
        st.subheader("✏️ Edit Emails")
        
        # Email selector with search
        search_term = st.text_input("🔍 Search emails", placeholder="Search by subject...")
        
        filtered_sequence = st.session_state.sequence
        if search_term:
            filtered_sequence = [e for e in st.session_state.sequence if search_term.lower() in e.get('subject', '').lower()]
        
        if filtered_sequence:
            email_options = [f"#{e.get('id')} - {e.get('subject')} (Day {e.get('delay')})" for e in filtered_sequence]
            selected_email_idx = st.selectbox(
                "Select Email",
                range(len(filtered_sequence)),
                format_func=lambda x: email_options[x],
                key='selected_email_idx'
            )
            
            email = filtered_sequence[selected_email_idx]
            actual_idx = st.session_state.sequence.index(email)
            
            # Validation warnings
            warnings = validate_email(email)
            if warnings:
                st.warning("⚠️ " + " | ".join(warnings))
            
            # Edit form with tabs
            edit_tab1, edit_tab2, edit_tab3 = st.tabs(["📝 Content", "📊 Stats", "👁️ Preview"])
            
            with edit_tab1:
                with st.form(f"edit_email_{actual_idx}", clear_on_submit=False):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        email['subject'] = st.text_input("Subject Line", value=email.get('subject', ''), max_chars=150)
                    
                    with col2:
                        email['delay'] = st.number_input("Delay (days)", min_value=0, value=email.get('delay', 0), step=1)
                    
                    with col3:
                        email['status'] = st.selectbox("Status", options=["active", "inactive", "draft"], 
                                                      index=["active", "inactive", "draft"].index(email.get('status', 'active')))
                    
                    # Extract content from HTML
                    content_match = re.search(r'<td style="padding: 40px 30px;">(.*?)</td>', email.get('email_body', ''), re.DOTALL)
                    current_content = content_match.group(1).strip() if content_match else ""
                    
                    st.markdown("**Email Content (HTML)**")
                    new_content = st.text_area(
                        "Content",
                        value=current_content,
                        height=400,
                        help="Enter HTML content for the email body",
                        label_visibility="collapsed"
                    )
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True):
                            email['email_body'] = create_email_html_template(new_content, header_img, footer_img)
                            st.session_state.sequence[actual_idx] = email
                            st.success("✅ Email updated!")
                            st.rerun()
                    
                    with col2:
                        if st.form_submit_button("🔄 Reset", use_container_width=True):
                            st.rerun()
                    
                    with col3:
                        if st.form_submit_button("👁️ Preview", use_container_width=True):
                            st.session_state.show_preview = actual_idx
            
            with edit_tab2:
                stats = analyze_email_content(email.get('email_body', ''))
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Words", stats['word_count'])
                col2.metric("Characters", stats['char_count'])
                col3.metric("Links", stats['link_count'])
                col4.metric("Images", stats['image_count'])
                
                st.info(f"📖 Estimated reading time: {stats['reading_time']} minute(s)")
                
                # Subject line analysis
                subject_len = len(email.get('subject', ''))
                if subject_len < 30:
                    st.warning(f"📧 Subject line is short ({subject_len} chars). Consider 30-50 characters for better engagement.")
                elif subject_len > 50:
                    st.warning(f"📧 Subject line is long ({subject_len} chars). May be truncated on mobile devices.")
                else:
                    st.success(f"📧 Subject line length is optimal ({subject_len} chars)")
            
            with edit_tab3:
                st.markdown("**HTML Preview:**")
                st.code(email.get('email_body', ''), language='html', line_numbers=True)
                
                st.markdown("**Rendered Preview:**")
                st.markdown(email.get('email_body', ''), unsafe_allow_html=True)
        else:
            st.info("No emails match your search")

with tab2:
    st.header("📚 Email Templates Library")
    st.markdown("Choose from pre-built templates to quickly create professional emails")
    
    categories = list(set([t['category'] for t in EMAIL_TEMPLATES.values()]))
    selected_category = st.selectbox("Filter by Category", ["All"] + sorted(categories))
    
    filtered_templates = EMAIL_TEMPLATES
    if selected_category != "All":
        filtered_templates = {k: v for k, v in EMAIL_TEMPLATES.items() if v['category'] == selected_category}
    
    cols = st.columns(2)
    for idx, (key, template) in enumerate(filtered_templates.items()):
        with cols[idx % 2]:
            with st.container():
                st.markdown(f"""
                <div class="template-card">
                    <h3 style="margin: 0 0 10px 0; color: #667eea;">{template['name']}</h3>
                    <p style="margin: 0 0 10px 0; color: #666; font-size: 14px;">
                        <strong>Category:</strong> {template['category']}<br>
                        <strong>Subject:</strong> {template['subject']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"👁️ Preview", key=f"preview_{key}", use_container_width=True):
                        st.session_state.preview_template = key
                
                with col2:
                    if st.button(f"➕ Use Template", key=f"use_{key}", use_container_width=True):
                        if 'sequence' not in st.session_state:
                            st.session_state.sequence = []
                        
                        new_id = max([e.get('id', 0) for e in st.session_state.sequence], default=0) + 1
                        new_email = {
                            "id": new_id,
                            "subject": template['subject'],
                            "email_body": create_email_html_template(template['content'], header_img, footer_img),
                            "delay": len(st.session_state.sequence),
                            "status": "active"
                        }
                        st.session_state.sequence.append(new_email)
                        st.success(f"✅ Added '{template['name']}' to sequence!")
                        st.rerun()
    
    # Template preview
    if 'preview_template' in st.session_state:
        st.divider()
        template = EMAIL_TEMPLATES[st.session_state.preview_template]
        st.subheader(f"Preview: {template['name']}")
        
        preview_html = create_email_html_template(template['content'], header_img, footer_img)
        
        preview_tab1, preview_tab2 = st.tabs(["Rendered", "HTML Code"])
        
        with preview_tab1:
            st.markdown(preview_html, unsafe_allow_html=True)
        
        with preview_tab2:
            st.code(preview_html, language='html', line_numbers=True)

with tab3:
    st.header("📊 Sequence Analytics")
    
    if 'sequence' in st.session_state and st.session_state.sequence:
        seq = st.session_state.sequence
        
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="stat-card">', unsafe_allow_html=True)
            st.metric("Total Emails", len(seq))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            active_count = sum(1 for e in seq if e.get('status') == 'active')
            st.markdown('<div class="stat-card">', unsafe_allow_html=True)
            st.metric("Active", active_count)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            total_days = max([e.get('delay', 0) for e in seq]) if seq else 0
            st.markdown('<div class="stat-card">', unsafe_allow_html=True)
            st.metric("Duration", f"{total_days} days")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            total_words = sum([analyze_email_content(e.get('email_body', ''))['word_count'] for e in seq])
            st.markdown('<div class="stat-card">', unsafe_allow_html=True)
            st.metric("Total Words", f"{total_words:,}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Detailed analytics
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Email Statistics")
            
            for email in seq:
                stats = analyze_email_content(email.get('email_body', ''))
                
                with st.expander(f"#{email.get('id')} - {email.get('subject')[:40]}..."):
                    col_a, col_b = st.columns(2)
                    col_a.metric("Words", stats['word_count'])
                    col_b.metric("Reading Time", f"{stats['reading_time']} min")
                    
                    col_c, col_d = st.columns(2)
                    col_c.metric("Links", stats['link_count'])
                    col_d.metric("Images", stats['image_count'])
                    
                    st.caption(f"Status: {email.get('status')} | Delay: {email.get('delay')} days")
        
        with col2:
            st.subheader("Content Distribution")
            
            # Word count distribution
            word_counts = [analyze_email_content(e.get('email_body', ''))['word_count'] for e in seq]
            avg_words = sum(word_counts) / len(word_counts) if word_counts else 0
            
            st.metric("Average Words per Email", f"{avg_words:.0f}")
            
            # Status distribution
            status_counts = Counter([e.get('status', 'unknown') for e in seq])
            st.markdown("**Status Breakdown:**")
            for status, count in status_counts.items():
                percentage = (count / len(seq)) * 100
                st.progress(percentage / 100, text=f"{status.capitalize()}: {count} ({percentage:.1f}%)")
            
            st.divider()
            
            # Delay distribution
            st.markdown("**Timing Distribution:**")
            delays = [e.get('delay', 0) for e in seq]
            st.write(f"- First email: Day {min(delays)}")
            st.write(f"- Last email: Day {max(delays)}")
            st.write(f"- Average gap: {(max(delays) / len(seq)):.1f} days")
    else:
        st.info("📭 No sequence loaded. Create or load a sequence to see analytics.")

with tab4:
    st.header("📅 Email Schedule Calculator")
    
    if 'sequence' in st.session_state and st.session_state.sequence:
        st.markdown("Calculate when each email will be sent based on a start date")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            start_date = st.date_input("Sequence Start Date", value=datetime.now())
            
            if st.button("📅 Calculate Schedule", type="primary", use_container_width=True):
                st.session_state.schedule = calculate_send_dates(
                    st.session_state.sequence,
                    datetime.combine(start_date, datetime.min.time())
                )
        
        with col2:
            if 'schedule' in st.session_state:
                st.subheader("Send Schedule")
                
                for item in st.session_state.schedule:
                    st.markdown(f"""
                    <div class="email-card">
                        <strong>Email #{item['email_id']}</strong>: {item['subject']}<br>
                        <span style="color: #667eea;">📅 {item['send_date']}</span> 
                        <span style="color: #999;">({item['days_from_start']} days from start)</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Export schedule
                st.divider()
                schedule_json = json.dumps(st.session_state.schedule, indent=2)
                st.download_button(
                    label="📥 Download Schedule (JSON)",
                    data=schedule_json,
                    file_name=f"email_schedule_{start_date}.json",
                    mime="application/json"
                )
    else:
        st.info("📭 No sequence loaded. Create or load a sequence to calculate schedule.")

with tab5:
    st.header("⚙️ Advanced Operations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔧 Bulk Operations")
        
        if 'sequence' in st.session_state and st.session_state.sequence:
            # Bulk status change
            st.markdown("**Change Status for All Emails:**")
            new_status = st.selectbox("New Status", ["active", "inactive", "draft"], key="bulk_status")
            if st.button("Apply to All", use_container_width=True):
                for email in st.session_state.sequence:
                    email['status'] = new_status
                st.success(f"✅ Changed all emails to '{new_status}'")
                st.rerun()
            
            st.divider()
            
            # Reorder emails
            st.markdown("**Reorder Emails:**")
            if st.button("🔢 Sort by Delay", use_container_width=True):
                st.session_state.sequence.sort(key=lambda x: x.get('delay', 0))
                st.success("✅ Sorted by delay")
                st.rerun()
            
            if st.button("🔢 Sort by ID", use_container_width=True):
                st.session_state.sequence.sort(key=lambda x: x.get('id', 0))
                st.success("✅ Sorted by ID")
                st.rerun()
            
            st.divider()
            
            # Renumber IDs
            st.markdown("**Renumber Email IDs:**")
            new_start_id = st.number_input("Start from ID", min_value=1, value=1)
            if st.button("🔢 Renumber", use_container_width=True):
                for idx, email in enumerate(st.session_state.sequence):
                    email['id'] = new_start_id + idx
                st.success("✅ Renumbered all emails")
                st.rerun()
        else:
            st.info("No sequence loaded")
    
    with col2:
        st.subheader("🔍 Validation & Quality Check")
        
        if 'sequence' in st.session_state and st.session_state.sequence:
            if st.button("🔍 Run Full Validation", type="primary", use_container_width=True):
                st.session_state.validation_results = []
                
                for email in st.session_state.sequence:
                    warnings = validate_email(email)
                    if warnings:
                        st.session_state.validation_results.append({
                            "email_id": email.get('id'),
                            "subject": email.get('subject'),
                            "warnings": warnings
                        })
            
            if 'validation_results' in st.session_state:
                if st.session_state.validation_results:
                    st.warning(f"⚠️ Found {len(st.session_state.validation_results)} emails with issues:")
                    
                    for result in st.session_state.validation_results:
                        with st.expander(f"Email #{result['email_id']}: {result['subject'][:40]}..."):
                            for warning in result['warnings']:
                                st.write(f"• {warning}")
                else:
                    st.success("✅ All emails passed validation!")
        else:
            st.info("No sequence loaded")
        
        st.divider()
        
        st.subheader("💾 Backup & Restore")
        
        if 'sequence' in st.session_state and st.session_state.sequence:
            if st.button("💾 Create Backup", use_container_width=True):
                backup_data = {
                    "timestamp": datetime.now().isoformat(),
                    "sequence": st.session_state.sequence
                }
                backup_json = json.dumps(backup_data, indent=2)
                st.download_button(
                    label="📥 Download Backup",
                    data=backup_json,
                    file_name=f"videmi_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )

if 'sequence' in st.session_state and st.session_state.sequence:
    st.divider()
    st.header("💾 Download Sequence")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        filename = st.text_input("Filename", value=f"email_sequence_{len(st.session_state.sequence)}_emails.json")
    
    with col2:
        indent = st.checkbox("Pretty Print", value=True)
    
    with col3:
        st.write("")  # Spacing
        json_str = json.dumps(st.session_state.sequence, indent=2 if indent else None)
        st.download_button(
            label="📥 Download JSON",
            data=json_str,
            file_name=filename,
            mime="application/json",
            type="primary",
            use_container_width=True
        )

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p><strong>VIDeMI Email Sequence Builder v2.0</strong> | Built with Streamlit</p>
    <p style='font-size: 14px; margin-top: 10px;'>
        Features: Template Library • Analytics • Schedule Calculator • Bulk Operations • Validation
    </p>
</div>
""", unsafe_allow_html=True)
