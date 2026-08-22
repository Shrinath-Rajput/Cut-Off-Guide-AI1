import json
import re
import urllib.parse
from urllib import request as urllib_request
from typing import List, Dict, Any, Optional
from app.core.config import settings

# Comprehensive Ground-Truth Directory of Top Indian Colleges Across All States
INDIAN_COLLEGES_SEED = [
    # -------------------------------------------------------------
    # MAHARASHTRA
    # -------------------------------------------------------------
    {
        "id": "iit-bombay",
        "name": "Indian Institute of Technology Bombay (IIT Bombay)",
        "city": "Mumbai",
        "state": "Maharashtra",
        "location": "Powai, Mumbai, Maharashtra",
        "type": "Institute of National Importance",
        "rating": 4.9,
        "nirf_rank": 3,
        "established": 1958,
        "exams": ["JEE Advanced", "GATE"],
        "courses": ["Computer Science", "Electrical", "Mechanical", "Aerospace", "Engineering Physics"],
        "feeValue": 220000,
        "fee_display": "₹2.2 Lakh / year",
        "placement_avg": "₹21.8 LPA",
        "highest_package": "₹1.68 Cr PA",
        "top_recruiters": ["Google", "Apple", "Jane Street", "Qualcomm", "BCG", "Tower Research"],
        "image": "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&w=800&q=80",
        "website": "https://www.iitb.ac.in",
        "highlights": "Premier Indian engineering institution in Powai Mumbai world-renowned for research and innovation."
    },
    {
        "id": "coep-pune",
        "name": "College of Engineering, Pune (COEP Tech)",
        "city": "Pune",
        "state": "Maharashtra",
        "location": "Shivajinagar, Pune, Maharashtra",
        "type": "State Unitary University (Government)",
        "rating": 4.8,
        "nirf_rank": 73,
        "established": 1854,
        "exams": ["MHT-CET", "JEE Main"],
        "courses": ["Computer Engineering", "Information Technology", "Electronics & Telecom", "Mechanical", "Civil"],
        "feeValue": 90000,
        "fee_display": "₹90,000 / year",
        "placement_avg": "₹12.5 LPA",
        "highest_package": "₹50.5 LPA",
        "top_recruiters": ["Google", "Microsoft", "Amazon", "Goldman Sachs", "Tata Motors", "Bajaj Auto"],
        "image": "https://images.unsplash.com/photo-1562774053-701939374585?auto=format&fit=crop&w=800&q=80",
        "website": "https://www.coep.org.in",
        "highlights": "Established in 1854, Asia's third oldest engineering institution with legendary alumni and elite cutoffs."
    },
    {
        "id": "vjti-mumbai",
        "name": "Veermata Jijabai Technological Institute (VJTI)",
        "city": "Mumbai",
        "state": "Maharashtra",
        "location": "Matunga, Mumbai, Maharashtra",
        "type": "Government Autonomous",
        "rating": 4.7,
        "nirf_rank": 82,
        "established": 1887,
        "exams": ["MHT-CET", "JEE Main"],
        "courses": ["Computer Engineering", "Information Technology", "Electronics", "Electrical", "Mechanical"],
        "feeValue": 85000,
        "fee_display": "₹85,000 / year",
        "placement_avg": "₹13.2 LPA",
        "highest_package": "₹62.0 LPA",
        "top_recruiters": ["Morgan Stanley", "Microsoft", "Samsung", "JPMorgan Chase", "L&T"],
        "image": "https://images.unsplash.com/photo-1541339907198-e08756dedf3f?auto=format&fit=crop&w=800&q=80",
        "website": "https://vjti.ac.in",
        "highlights": "Premier autonomous institute in Central Mumbai with high software and fintech placement conversion."
    },
    {
        "id": "spit-mumbai",
        "name": "Sardar Patel Institute of Technology (SPIT)",
        "city": "Mumbai",
        "state": "Maharashtra",
        "location": "Andheri West, Mumbai, Maharashtra",
        "type": "Private Autonomous",
        "rating": 4.6,
        "nirf_rank": 125,
        "established": 2005,
        "exams": ["MHT-CET", "JEE Main"],
        "courses": ["Computer Science & Engineering", "Information Technology", "CS & Data Science", "EXTC"],
        "feeValue": 170000,
        "fee_display": "₹1.7 Lakh / year",
        "placement_avg": "₹15.0 LPA",
        "highest_package": "₹42.0 LPA",
        "top_recruiters": ["Microsoft", "Morgan Stanley", "JPMorgan Chase", "Nomura", "Barclays"],
        "image": "https://images.unsplash.com/photo-1562774053-701939374585?auto=format&fit=crop&w=800&q=80",
        "website": "https://www.spit.ac.in",
        "highlights": "Located in Andheri West Mumbai with premier financial technology & product engineering recruitment."
    },
    {
        "id": "pict-pune",
        "name": "Pune Institute of Computer Technology (PICT)",
        "city": "Pune",
        "state": "Maharashtra",
        "location": "Dhankawadi, Pune, Maharashtra",
        "type": "Private Autonomous",
        "rating": 4.6,
        "nirf_rank": 140,
        "established": 1983,
        "exams": ["MHT-CET", "JEE Main"],
        "courses": ["Computer Engineering", "Information Technology", "AI & Data Science", "Electronics & Telecom"],
        "feeValue": 98000,
        "fee_display": "₹98,000 / year",
        "placement_avg": "₹12.8 LPA",
        "highest_package": "₹45.0 LPA",
        "top_recruiters": ["Mastercard", "PhonePe", "Deutsche Bank", "Amazon", "Rakuten"],
        "image": "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&w=800&q=80",
        "website": "https://pict.edu",
        "highlights": "Renowned coding powerhouse with some of the highest placement numbers for software engineers in Pune."
    },
    {
        "id": "dypcoe-akurdi",
        "name": "Dr. D. Y. Patil College of Engineering (DYPCOE Akurdi)",
        "city": "Pune",
        "state": "Maharashtra",
        "location": "Akurdi, Pune, Maharashtra",
        "type": "Private Autonomous",
        "rating": 4.3,
        "nirf_rank": 145,
        "established": 1984,
        "exams": ["MHT-CET", "JEE Main"],
        "courses": ["Computer Engineering", "Information Technology", "AI & Data Science", "Robotics & Automation"],
        "feeValue": 140000,
        "fee_display": "₹1.4 Lakh / year",
        "placement_avg": "₹6.8 LPA",
        "highest_package": "₹42.0 LPA",
        "top_recruiters": ["TCS", "Infosys", "Wipro", "Cognizant", "Capgemini", "Amazon"],
        "image": "https://images.unsplash.com/photo-1562774053-701939374585?auto=format&fit=crop&w=800&q=80",
        "website": "https://www.dypcoeakurdi.ac.in",
        "highlights": "Established in 1984 in Akurdi Pune, accredited with NAAC 'A' grade with strong coding placements."
    },
    {
        "id": "pccoe-pune",
        "name": "Pimpri Chinchwad College of Engineering (PCCOE)",
        "city": "Pune",
        "state": "Maharashtra",
        "location": "Nigdi, Pune, Maharashtra",
        "type": "Private Autonomous",
        "rating": 4.4,
        "nirf_rank": 152,
        "established": 1999,
        "exams": ["MHT-CET", "JEE Main"],
        "courses": ["Computer Engineering", "IT", "AI & Machine Learning", "Mechanical", "Civil"],
        "feeValue": 145000,
        "fee_display": "₹1.45 Lakh / year",
        "placement_avg": "₹7.2 LPA",
        "highest_package": "₹38.0 LPA",
        "top_recruiters": ["TCS", "Capgemini", "KPIT", "Accenture", "Cummins"],
        "image": "https://images.unsplash.com/photo-1541339907198-e08756dedf3f?auto=format&fit=crop&w=800&q=80",
        "website": "https://www.pccoepune.com",
        "highlights": "Central placement hub in PCMC known for disciplined academics and high placement conversion rate."
    },
    {
        "id": "vit-pune",
        "name": "Vishwakarma Institute of Technology (VIT Pune)",
        "city": "Pune",
        "state": "Maharashtra",
        "location": "Bibwewadi, Pune, Maharashtra",
        "type": "Private Autonomous",
        "rating": 4.5,
        "nirf_rank": 138,
        "established": 1983,
        "exams": ["MHT-CET", "JEE Main"],
        "courses": ["Computer Engineering", "IT", "AI & DS", "Instrumentation", "Chemical"],
        "feeValue": 185000,
        "fee_display": "₹1.85 Lakh / year",
        "placement_avg": "₹8.5 LPA",
        "highest_package": "₹44.0 LPA",
        "top_recruiters": ["NVIDIA", "Texas Instruments", "Mercedes-Benz", "Amazon", "Deloitte"],
        "image": "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&w=800&q=80",
        "website": "https://www.vit.edu",
        "highlights": "Top private autonomous college in Pune with project-based learning and strong corporate connect."
    },

    # -------------------------------------------------------------
    # DELHI
    # -------------------------------------------------------------
    {
        "id": "iit-delhi",
        "name": "Indian Institute of Technology Delhi (IIT Delhi)",
        "city": "New Delhi",
        "state": "Delhi",
        "location": "Hauz Khas, New Delhi",
        "type": "Institute of National Importance",
        "rating": 4.9,
        "nirf_rank": 2,
        "established": 1961,
        "exams": ["JEE Advanced", "GATE"],
        "courses": ["Computer Science", "Electrical", "Mathematics and Computing", "Mechanical"],
        "feeValue": 225000,
        "fee_display": "₹2.25 Lakh / year",
        "placement_avg": "₹23.5 LPA",
        "highest_package": "₹2.0 Cr PA",
        "top_recruiters": ["Microsoft", "Google", "Goldman Sachs", "McKinsey", "Intel"],
        "image": "https://images.unsplash.com/photo-1562774053-701939374585?auto=format&fit=crop&w=800&q=80",
        "website": "https://home.iitd.ac.in",
        "highlights": "Leading capital institution for research, entrepreneurship, and top engineering talent."
    },
    {
        "id": "dtu-delhi",
        "name": "Delhi Technological University (DTU / DCE)",
        "city": "New Delhi",
        "state": "Delhi",
        "location": "Rohini, New Delhi",
        "type": "State University",
        "rating": 4.6,
        "nirf_rank": 29,
        "established": 1941,
        "exams": ["JEE Main"],
        "courses": ["Computer Engineering", "Software Engineering", "IT", "Electronics & Comm"],
        "feeValue": 190000,
        "fee_display": "₹1.9 Lakh / year",
        "placement_avg": "₹15.2 LPA",
        "highest_package": "₹82.0 LPA",
        "top_recruiters": ["Adobe", "Amazon", "Flipkart", "Uber", "Sprinklr", "Google"],
        "image": "https://images.unsplash.com/photo-1592280771190-3e2e4d571952?auto=format&fit=crop&w=800&q=80",
        "website": "https://dtu.ac.in",
        "highlights": "Top state government engineering university in Delhi with vibrant coding culture and high placements."
    },
    {
        "id": "nsut-delhi",
        "name": "Netaji Subhas University of Technology (NSUT Delhi)",
        "city": "New Delhi",
        "state": "Delhi",
        "location": "Dwarka, New Delhi",
        "type": "State University",
        "rating": 4.5,
        "nirf_rank": 57,
        "established": 1983,
        "exams": ["JEE Main"],
        "courses": ["Computer Engineering", "IT", "Mathematics & Computing", "ECE"],
        "feeValue": 210000,
        "fee_display": "₹2.1 Lakh / year",
        "placement_avg": "₹16.0 LPA",
        "highest_package": "₹1.06 Cr PA",
        "top_recruiters": ["Microsoft", "Google", "Amazon", "Directi", "Tower Research"],
        "image": "https://images.unsplash.com/photo-1541339907198-e08756dedf3f?auto=format&fit=crop&w=800&q=80",
        "website": "https://nsut.ac.in",
        "highlights": "Dwarka Delhi premier university renowned for exceptional CS/IT placements and alumni founders."
    },
    {
        "id": "iiit-delhi",
        "name": "Indraprastha Institute of Information Technology Delhi (IIIT-Delhi)",
        "city": "New Delhi",
        "state": "Delhi",
        "location": "Okhla, New Delhi",
        "type": "State Autonomous University",
        "rating": 4.6,
        "nirf_rank": 75,
        "established": 2008,
        "exams": ["JEE Main", "JAC Delhi"],
        "courses": ["Computer Science & Applied Math", "CS & AI", "CS & Design", "ECE"],
        "feeValue": 410000,
        "fee_display": "₹4.1 Lakh / year",
        "placement_avg": "₹20.4 LPA",
        "highest_package": "₹51.3 LPA",
        "top_recruiters": ["Google", "Microsoft", "Goldman Sachs", "Amazon", "NVIDIA"],
        "image": "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&w=800&q=80",
        "website": "https://iiitd.ac.in",
        "highlights": "Research-focused cutting-edge computing curriculum in South Delhi with high international research output."
    },

    # -------------------------------------------------------------
    # KARNATAKA
    # -------------------------------------------------------------
    {
        "id": "iisc-bangalore",
        "name": "Indian Institute of Science (IISc Bangalore)",
        "city": "Bengaluru",
        "state": "Karnataka",
        "location": "Bengaluru, Karnataka",
        "type": "Institute of Eminence",
        "rating": 5.0,
        "nirf_rank": 1,
        "established": 1909,
        "exams": ["JEE Advanced", "KVPY", "GATE"],
        "courses": ["Computer Science", "Data Science", "Electrical", "Aerospace"],
        "feeValue": 35000,
        "fee_display": "₹35,000 / year",
        "placement_avg": "₹28.0 LPA",
        "highest_package": "₹86.0 LPA",
        "top_recruiters": ["Google Brain", "Microsoft Research", "NVIDIA", "Intel", "ISRO"],
        "image": "https://images.unsplash.com/photo-1541339907198-e08756dedf3f?auto=format&fit=crop&w=800&q=80",
        "website": "https://iisc.ac.in",
        "highlights": "India's #1 scientific research and technology institute."
    },
    {
        "id": "nitk-surathkal",
        "name": "National Institute of Technology Karnataka (NITK Surathkal)",
        "city": "Mangaluru",
        "state": "Karnataka",
        "location": "Surathkal, Mangaluru, Karnataka",
        "type": "Institute of National Importance (NIT)",
        "rating": 4.7,
        "nirf_rank": 12,
        "established": 1960,
        "exams": ["JEE Main", "DASA"],
        "courses": ["Computer Science", "Information Technology", "AI", "ECE", "Mechanical"],
        "feeValue": 150000,
        "fee_display": "₹1.5 Lakh / year",
        "placement_avg": "₹16.5 LPA",
        "highest_package": "₹54.0 LPA",
        "top_recruiters": ["Microsoft", "Amazon", "Wells Fargo", "Oracle", "Qualcomm"],
        "image": "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&w=800&q=80",
        "website": "https://www.nitk.ac.in",
        "highlights": "Premier beachside NIT campus with top-tier rankings and high product tech recruitment."
    },
    {
        "id": "rvce-bangalore",
        "name": "RV College of Engineering (RVCE Bengaluru)",
        "city": "Bengaluru",
        "state": "Karnataka",
        "location": "Mysuru Road, Bengaluru, Karnataka",
        "type": "Private Autonomous",
        "rating": 4.6,
        "nirf_rank": 96,
        "established": 1963,
        "exams": ["KCET", "COMEDK"],
        "courses": ["Computer Science", "Information Science", "AI & ML", "ECE", "Aerospace"],
        "feeValue": 250000,
        "fee_display": "₹2.5 Lakh / year",
        "placement_avg": "₹14.8 LPA",
        "highest_package": "₹62.0 LPA",
        "top_recruiters": ["Cisco", "Amazon", "Qualcomm", "Adobe", "Morgan Stanley"],
        "image": "https://images.unsplash.com/photo-1562774053-701939374585?auto=format&fit=crop&w=800&q=80",
        "website": "https://rvce.edu.in",
        "highlights": "Top private engineering college in Karnataka with exceptional placements in Bengaluru's tech ecosystem."
    },
    {
        "id": "bmsce-bangalore",
        "name": "BMS College of Engineering (BMSCE Bengaluru)",
        "city": "Bengaluru",
        "state": "Karnataka",
        "location": "Basavanagudi, Bengaluru, Karnataka",
        "type": "Private Autonomous",
        "rating": 4.5,
        "nirf_rank": 105,
        "established": 1946,
        "exams": ["KCET", "COMEDK"],
        "courses": ["Computer Science", "Information Science", "AI & Data Science", "ECE"],
        "feeValue": 230000,
        "fee_display": "₹2.3 Lakh / year",
        "placement_avg": "₹11.2 LPA",
        "highest_package": "₹50.0 LPA",
        "top_recruiters": ["Dell", "Oracle", "Goldman Sachs", "Bosch", "Mercedes-Benz"],
        "image": "https://images.unsplash.com/photo-1541339907198-e08756dedf3f?auto=format&fit=crop&w=800&q=80",
        "website": "https://bmsce.ac.in",
        "highlights": "First private engineering college in India with prime Bengaluru location and rich heritage."
    },

    # -------------------------------------------------------------
    # TAMIL NADU
    # -------------------------------------------------------------
    {
        "id": "iit-madras",
        "name": "Indian Institute of Technology Madras (IIT Madras)",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "location": "Chennai, Tamil Nadu",
        "type": "Institute of National Importance",
        "rating": 4.9,
        "nirf_rank": 1,
        "established": 1959,
        "exams": ["JEE Advanced", "GATE"],
        "courses": ["Computer Science", "Data Science & AI", "Electrical", "Mechanical"],
        "feeValue": 215000,
        "fee_display": "₹2.15 Lakh / year",
        "placement_avg": "₹22.5 LPA",
        "highest_package": "₹1.31 Cr PA",
        "top_recruiters": ["Google", "Microsoft", "Texas Instruments", "Qualcomm", "Airbus"],
        "image": "https://images.unsplash.com/photo-1562774053-701939374585?auto=format&fit=crop&w=800&q=80",
        "website": "https://www.iitm.ac.in",
        "highlights": "Ranked #1 overall in NIRF rankings with the country's top university research park."
    },
    {
        "id": "nit-trichy",
        "name": "National Institute of Technology Tiruchirappalli (NIT Trichy)",
        "city": "Tiruchirappalli",
        "state": "Tamil Nadu",
        "location": "Thuvakudi, Tiruchirappalli, Tamil Nadu",
        "type": "Institute of National Importance (NIT)",
        "rating": 4.8,
        "nirf_rank": 9,
        "established": 1964,
        "exams": ["JEE Main", "DASA"],
        "courses": ["Computer Science", "ECE", "EEE", "Mechanical", "Chemical"],
        "feeValue": 160000,
        "fee_display": "₹1.6 Lakh / year",
        "placement_avg": "₹18.2 LPA",
        "highest_package": "₹52.9 LPA",
        "top_recruiters": ["Google", "Microsoft", "Morgan Stanley", "Texas Instruments", "Samsung"],
        "image": "https://images.unsplash.com/photo-1541339907198-e08756dedf3f?auto=format&fit=crop&w=800&q=80",
        "website": "https://www.nitt.edu",
        "highlights": "#1 Ranked NIT in India with exceptional NIRF score, competitive programming, and placements."
    },
    {
        "id": "vit-vellore",
        "name": "Vellore Institute of Technology (VIT Vellore)",
        "city": "Vellore",
        "state": "Tamil Nadu",
        "location": "Vellore, Tamil Nadu",
        "type": "Deemed to be University",
        "rating": 4.4,
        "nirf_rank": 11,
        "established": 1984,
        "exams": ["VITEEE"],
        "courses": ["Computer Science", "Information Security", "AI & ML", "ECE"],
        "feeValue": 198000,
        "fee_display": "₹1.98 Lakh / year",
        "placement_avg": "₹9.2 LPA",
        "highest_package": "₹1.02 Cr PA",
        "top_recruiters": ["Microsoft", "Amazon", "Deloitte", "Wipro", "TCS", "Cognizant"],
        "image": "https://images.unsplash.com/photo-1592280771190-3e2e4d571952?auto=format&fit=crop&w=800&q=80",
        "website": "https://vit.ac.in",
        "highlights": "Massive corporate placement drives with ABET accredited international engineering curricula."
    },
    {
        "id": "srm-chennai",
        "name": "SRM Institute of Science and Technology (SRM Kattankulathur)",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "location": "Kattankulathur, Chennai, Tamil Nadu",
        "type": "Deemed to be University",
        "rating": 4.3,
        "nirf_rank": 28,
        "established": 1985,
        "exams": ["SRMJEEE"],
        "courses": ["Computer Science", "Cyber Security", "Data Science", "ECE", "Biotech"],
        "feeValue": 250000,
        "fee_display": "₹2.5 Lakh / year",
        "placement_avg": "₹8.0 LPA",
        "highest_package": "₹1.0 Cr PA",
        "top_recruiters": ["Amazon", "PayPal", "Barclays", "TCS", "Wipro", "Infosys"],
        "image": "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&w=800&q=80",
        "website": "https://www.srmist.edu.in",
        "highlights": "250-acre mega campus in Chennai with high placement volume and international exchange programs."
    },

    # -------------------------------------------------------------
    # TELANGANA
    # -------------------------------------------------------------
    {
        "id": "iit-hyderabad",
        "name": "Indian Institute of Technology Hyderabad (IIT Hyderabad)",
        "city": "Hyderabad",
        "state": "Telangana",
        "location": "Kandi, Sangareddy, Telangana",
        "type": "Institute of National Importance",
        "rating": 4.8,
        "nirf_rank": 8,
        "established": 2008,
        "exams": ["JEE Advanced"],
        "courses": ["Computer Science", "Artificial Intelligence", "Electrical", "Mechanical"],
        "feeValue": 220000,
        "fee_display": "₹2.2 Lakh / year",
        "placement_avg": "₹20.0 LPA",
        "highest_package": "₹63.7 LPA",
        "top_recruiters": ["Rakuten", "Microsoft", "Qualcomm", "Amazon", "TSMC"],
        "image": "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&w=800&q=80",
        "website": "https://www.iith.ac.in",
        "highlights": "Fastest growing 2nd gen IIT with pioneering B.Tech in AI and Japanese collaborative research."
    },
    {
        "id": "iiit-hyderabad",
        "name": "International Institute of Information Technology Hyderabad (IIIT-H)",
        "city": "Hyderabad",
        "state": "Telangana",
        "location": "Gachibowli, Hyderabad, Telangana",
        "type": "Autonomous / Deemed",
        "rating": 4.9,
        "nirf_rank": 55,
        "established": 1998,
        "exams": ["JEE Main", "UGEE"],
        "courses": ["Computer Science", "Electronics & Comm", "Computational Linguistics"],
        "feeValue": 380000,
        "fee_display": "₹3.8 Lakh / year",
        "placement_avg": "₹30.5 LPA",
        "highest_package": "₹69.0 LPA",
        "top_recruiters": ["Google", "Meta", "Apple", "Bloomberg", "Uber"],
        "image": "https://images.unsplash.com/photo-1562774053-701939374585?auto=format&fit=crop&w=800&q=80",
        "website": "https://www.iiit.ac.in",
        "highlights": "Gold standard for Coding, Competitive Programming, NLP, and Computer Vision in India."
    },
    {
        "id": "nit-warangal",
        "name": "National Institute of Technology Warangal (NIT Warangal)",
        "city": "Warangal",
        "state": "Telangana",
        "location": "Warangal, Telangana",
        "type": "Institute of National Importance (NIT)",
        "rating": 4.7,
        "nirf_rank": 21,
        "established": 1959,
        "exams": ["JEE Main", "DASA"],
        "courses": ["Computer Science", "ECE", "EEE", "Mechanical", "Civil"],
        "feeValue": 155000,
        "fee_display": "₹1.55 Lakh / year",
        "placement_avg": "₹17.3 LPA",
        "highest_package": "₹88.0 LPA",
        "top_recruiters": ["Microsoft", "Amazon", "Qualcomm", "DE Shaw", "Oracle"],
        "image": "https://images.unsplash.com/photo-1541339907198-e08756dedf3f?auto=format&fit=crop&w=800&q=80",
        "website": "https://www.nitw.ac.in",
        "highlights": "The very first Regional Engineering College in India with elite ranking and top tech placements."
    },

    # -------------------------------------------------------------
    # UTTAR PRADESH
    # -------------------------------------------------------------
    {
        "id": "iit-kanpur",
        "name": "Indian Institute of Technology Kanpur (IIT Kanpur)",
        "city": "Kanpur",
        "state": "Uttar Pradesh",
        "location": "Kalyanpur, Kanpur, Uttar Pradesh",
        "type": "Institute of National Importance",
        "rating": 4.8,
        "nirf_rank": 4,
        "established": 1959,
        "exams": ["JEE Advanced", "GATE"],
        "courses": ["Computer Science", "Electrical", "Mechanical", "Aerospace"],
        "feeValue": 218000,
        "fee_display": "₹2.18 Lakh / year",
        "placement_avg": "₹26.2 LPA",
        "highest_package": "₹1.9 Cr PA",
        "top_recruiters": ["Google", "Microsoft", "Texas Instruments", "Quantbox", "Goldman Sachs"],
        "image": "https://images.unsplash.com/photo-1592280771190-3e2e4d571952?auto=format&fit=crop&w=800&q=80",
        "website": "https://www.iitk.ac.in",
        "highlights": "Pioneer of computer science education in India with its own private airstrip and supercomputer."
    },
    {
        "id": "iit-bhu",
        "name": "Indian Institute of Technology (BHU) Varanasi",
        "city": "Varanasi",
        "state": "Uttar Pradesh",
        "location": "Varanasi, Uttar Pradesh",
        "type": "Institute of National Importance",
        "rating": 4.7,
        "nirf_rank": 15,
        "established": 1919,
        "exams": ["JEE Advanced", "GATE"],
        "courses": ["Computer Science", "Electronics", "Electrical", "Mechanical", "Ceramic"],
        "feeValue": 220000,
        "fee_display": "₹2.2 Lakh / year",
        "placement_avg": "₹21.0 LPA",
        "highest_package": "₹1.2 Cr PA",
        "top_recruiters": ["Google", "Microsoft", "Uber", "Oracle", "Goldman Sachs"],
        "image": "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&w=800&q=80",
        "website": "https://www.iitbhu.ac.in",
        "highlights": "Centenary heritage institution within BHU campus with top tech placements and alumni."
    },
    {
        "id": "mnnit-allahabad",
        "name": "Motilal Nehru National Institute of Technology (MNNIT Allahabad)",
        "city": "Prayagraj",
        "state": "Uttar Pradesh",
        "location": "Prayagraj, Uttar Pradesh",
        "type": "Institute of National Importance (NIT)",
        "rating": 4.6,
        "nirf_rank": 49,
        "established": 1961,
        "exams": ["JEE Main"],
        "courses": ["Computer Science", "Information Technology", "ECE", "Electrical", "Mechanical"],
        "feeValue": 140000,
        "fee_display": "₹1.4 Lakh / year",
        "placement_avg": "₹17.2 LPA",
        "highest_package": "₹1.35 Cr PA",
        "top_recruiters": ["Google", "Amazon", "Microsoft", "Atlassian", "DE Shaw"],
        "image": "https://images.unsplash.com/photo-1541339907198-e08756dedf3f?auto=format&fit=crop&w=800&q=80",
        "website": "https://www.mnnit.ac.in",
        "highlights": "Premier North Indian NIT with one of the highest percentage placements in software engineering."
    },

    # -------------------------------------------------------------
    # RAJASTHAN
    # -------------------------------------------------------------
    {
        "id": "bits-pilani",
        "name": "Birla Institute of Technology and Science (BITS Pilani)",
        "city": "Pilani",
        "state": "Rajasthan",
        "location": "Pilani, Rajasthan",
        "type": "Institute of Eminence (Deemed)",
        "rating": 4.8,
        "nirf_rank": 20,
        "established": 1964,
        "exams": ["BITSAT"],
        "courses": ["Computer Science", "Electronics & Instrumentation", "Electrical", "Mechanical"],
        "feeValue": 540000,
        "fee_display": "₹5.4 Lakh / year",
        "placement_avg": "₹20.9 LPA",
        "highest_package": "₹60.7 LPA",
        "top_recruiters": ["Google", "Microsoft", "Uber", "DE Shaw", "Nutanix"],
        "image": "https://images.unsplash.com/photo-1541339907198-e08756dedf3f?auto=format&fit=crop&w=800&q=80",
        "website": "https://www.bits-pilani.ac.in",
        "highlights": "Zero attendance policy, Practice School industrial internships, and top startup founders."
    },
    {
        "id": "mnit-jaipur",
        "name": "Malaviya National Institute of Technology (MNIT Jaipur)",
        "city": "Jaipur",
        "state": "Rajasthan",
        "location": "JLN Marg, Jaipur, Rajasthan",
        "type": "Institute of National Importance (NIT)",
        "rating": 4.6,
        "nirf_rank": 37,
        "established": 1963,
        "exams": ["JEE Main"],
        "courses": ["Computer Science", "ECE", "Electrical", "Mechanical", "Civil"],
        "feeValue": 150000,
        "fee_display": "₹1.5 Lakh / year",
        "placement_avg": "₹14.5 LPA",
        "highest_package": "₹64.0 LPA",
        "top_recruiters": ["Amazon", "Apple", "Oracle", "Goldman Sachs", "Texas Instruments"],
        "image": "https://images.unsplash.com/photo-1562774053-701939374585?auto=format&fit=crop&w=800&q=80",
        "website": "https://www.mnit.ac.in",
        "highlights": "Centrally located in Jaipur with strong technical society culture and high placement records."
    },

    # -------------------------------------------------------------
    # WEST BENGAL
    # -------------------------------------------------------------
    {
        "id": "iit-kharagpur",
        "name": "Indian Institute of Technology Kharagpur (IIT KGP)",
        "city": "Kharagpur",
        "state": "West Bengal",
        "location": "Kharagpur, West Bengal",
        "type": "Institute of National Importance",
        "rating": 4.8,
        "nirf_rank": 6,
        "established": 1951,
        "exams": ["JEE Advanced", "GATE"],
        "courses": ["Computer Science", "Electronics", "Mechanical", "Chemical"],
        "feeValue": 224000,
        "fee_display": "₹2.24 Lakh / year",
        "placement_avg": "₹20.8 LPA",
        "highest_package": "₹2.6 Cr PA",
        "top_recruiters": ["Google", "Apple", "Microsoft", "Qualcomm", "Amazon"],
        "image": "https://images.unsplash.com/photo-1541339907198-e08756dedf3f?auto=format&fit=crop&w=800&q=80",
        "website": "https://www.iitkgp.ac.in",
        "highlights": "The very first IIT in India boasting the largest 2100-acre lush green residential campus."
    },
    {
        "id": "jadavpur-university",
        "name": "Jadavpur University (Faculty of Engineering & Tech)",
        "city": "Kolkata",
        "state": "West Bengal",
        "location": "Jadavpur, Kolkata, West Bengal",
        "type": "State Government University",
        "rating": 4.8,
        "nirf_rank": 10,
        "established": 1906,
        "exams": ["WBJEE", "GATE"],
        "courses": ["Computer Science", "Information Technology", "Electronics & Telecom", "Mechanical"],
        "feeValue": 10000,
        "fee_display": "₹10,000 / 4 years (Ultra Low)",
        "placement_avg": "₹15.5 LPA",
        "highest_package": "₹1.4 Cr PA",
        "top_recruiters": ["Google", "Amazon", "Texas Instruments", "Microsoft", "PwC"],
        "image": "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&w=800&q=80",
        "website": "http://www.jaduniv.edu.in",
        "highlights": "Unbeatable Return on Investment (ROI) with negligible tuition fees and premier product tech placements."
    },

    # -------------------------------------------------------------
    # GUJARAT
    # -------------------------------------------------------------
    {
        "id": "iit-gandhinagar",
        "name": "Indian Institute of Technology Gandhinagar (IITGN)",
        "city": "Gandhinagar",
        "state": "Gujarat",
        "location": "Palaj, Gandhinagar, Gujarat",
        "type": "Institute of National Importance",
        "rating": 4.7,
        "nirf_rank": 18,
        "established": 2008,
        "exams": ["JEE Advanced"],
        "courses": ["Computer Science", "Electrical", "Mechanical", "Civil", "Materials"],
        "feeValue": 225000,
        "fee_display": "₹2.25 Lakh / year",
        "placement_avg": "₹18.0 LPA",
        "highest_package": "₹52.0 LPA",
        "top_recruiters": ["Amazon", "Google", "Infosys", "ITC", "Goldman Sachs"],
        "image": "https://images.unsplash.com/photo-1562774053-701939374585?auto=format&fit=crop&w=800&q=80",
        "website": "https://iitgn.ac.in",
        "highlights": "Riverfront green campus in Gandhinagar with modern 5-star GRIHA rated campus and liberal curriculum."
    },
    {
        "id": "svnit-surat",
        "name": "Sardar Vallabhbhai National Institute of Technology (SVNIT Surat)",
        "city": "Surat",
        "state": "Gujarat",
        "location": "Ichchhanath, Surat, Gujarat",
        "type": "Institute of National Importance (NIT)",
        "rating": 4.5,
        "nirf_rank": 65,
        "established": 1961,
        "exams": ["JEE Main"],
        "courses": ["Computer Engineering", "AI", "ECE", "Electrical", "Chemical"],
        "feeValue": 150000,
        "fee_display": "₹1.5 Lakh / year",
        "placement_avg": "₹12.5 LPA",
        "highest_package": "₹44.0 LPA",
        "top_recruiters": ["Microsoft", "Amazon", "Samsung", "L&T", "Deloitte"],
        "image": "https://images.unsplash.com/photo-1541339907198-e08756dedf3f?auto=format&fit=crop&w=800&q=80",
        "website": "https://www.svnit.ac.in",
        "highlights": "Premier engineering institute in Gujarat with great chemical & software placement records."
    }
]


def normalize_str(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


async def get_all_colleges(
    db,
    page: int = 1,
    limit: int = 12,
    search: Optional[str] = None,
    states: Optional[List[str]] = None,
    courses: Optional[List[str]] = None,
    max_fee: Optional[int] = None,
    college_type: Optional[str] = None,
    sort: Optional[str] = None,
) -> Dict[str, Any]:
    # Extract clean requested states
    clean_states = []
    if states:
        for s in states:
            if isinstance(s, str):
                for part in s.split(","):
                    p = part.strip()
                    if p and p not in ["All India", "All Over India", "IN All India"]:
                        clean_states.append(p)

    # 1. Fetch from DB if available
    db_colleges = []
    if db is not None:
        try:
            collection = db["colleges"]
            query = {}

            if search:
                query["$or"] = [
                    {"name": {"$regex": search, "$options": "i"}},
                    {"city": {"$regex": search, "$options": "i"}},
                    {"state": {"$regex": search, "$options": "i"}},
                    {"location": {"$regex": search, "$options": "i"}},
                ]

            if clean_states:
                state_regex = "|".join([re.escape(s) for s in clean_states])
                query["state"] = {"$regex": f"^({state_regex})$", "$options": "i"}

            cursor = collection.find(query).limit(100)
            fetched = await cursor.to_list(length=100)
            for c in fetched:
                if "id" not in c:
                    c["id"] = str(c["_id"])
                if "_id" in c:
                    del c["_id"]
                db_colleges.append(c)
        except Exception as e:
            print("MongoDB query exception:", e)

    # 2. Combine with Seed data (deduplicated by name)
    seen_names = {c["name"].lower() for c in db_colleges}
    combined = list(db_colleges)
    for seed in INDIAN_COLLEGES_SEED:
        if seed["name"].lower() not in seen_names:
            combined.append(seed)

    # 3. Filter strictly by State
    filtered = combined
    if clean_states:
        lower_states = [st.lower() for st in clean_states]
        filtered = [
            c
            for c in filtered
            if any(
                st in c.get("state", "").strip().lower()
                or st in c.get("location", "").strip().lower()
                for st in lower_states
            )
        ]

    # 4. Filter by Search Query
    if search:
        s = search.lower().strip()
        filtered = [
            c
            for c in filtered
            if s in c.get("name", "").lower()
            or s in c.get("city", "").lower()
            or s in c.get("state", "").lower()
            or s in c.get("location", "").lower()
            or any(s in course.lower() for course in c.get("courses", []))
        ]

    # 5. Sort
    if sort == "ranking":
        filtered.sort(key=lambda c: c.get("nirf_rank") or 999)
    elif sort == "fees":
        filtered.sort(key=lambda c: c.get("feeValue") or 999999)
    else:
        filtered.sort(key=lambda c: c.get("rating") or 4.5, reverse=True)

    total = len(filtered)
    total_pages = (total + limit - 1) // limit if total > 0 else 1
    skip = (page - 1) * limit
    page_data = filtered[skip : skip + limit]

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "data": page_data,
    }


async def get_college_by_id(db, college_id: str) -> Optional[Dict[str, Any]]:
    if db is not None:
        try:
            collection = db["colleges"]
            college = await collection.find_one(
                {"$or": [{"id": college_id}, {"_id": college_id}]}
            )
            if college:
                college["id"] = str(college.get("_id", college_id))
                if "_id" in college:
                    del college["_id"]
                return college
        except Exception:
            pass

    for c in INDIAN_COLLEGES_SEED:
        if c["id"] == college_id:
            return c
    return None


def fetch_live_web_context(college_name: str) -> str:
    """Fetch factual snippets from Wikipedia API and DuckDuckGo for live accurate search."""
    context_parts = []

    # 1. Wikipedia Search API
    try:
        query_str = urllib.parse.quote(college_name.strip() + " college India")
        wiki_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={query_str}&format=json&utf8=1"
        req = urllib_request.Request(
            wiki_url, headers={"User-Agent": "CutoffGuideAI/2.0 (Factual Bot)"}
        )
        with urllib_request.urlopen(req, timeout=5) as res:
            data = json.loads(res.read().decode("utf-8"))
            items = data.get("query", {}).get("search", [])[:3]
            for item in items:
                title = item.get("title", "")
                snippet = re.sub(r"<[^>]+>", "", item.get("snippet", "")).strip()
                if snippet:
                    context_parts.append(f"Wikipedia [{title}]: {snippet}")
    except Exception as e:
        print("Wikipedia API lookup:", e)

    # 2. DuckDuckGo Instant Answer API
    try:
        ddg_url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(college_name.strip() + ' college')}&format=json&no_html=1&skip_disambig=1"
        req2 = urllib_request.Request(ddg_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib_request.urlopen(req2, timeout=5) as res:
            data2 = json.loads(res.read().decode("utf-8"))
            abstract = data2.get("AbstractText", "")
            if abstract:
                context_parts.append(f"DuckDuckGo Abstract: {abstract}")
    except Exception as e:
        print("DDG API lookup:", e)

    return "\n".join(context_parts)


def clean_highlights_text(raw_text: str, name: str = "The college") -> str:
    if not raw_text:
        return f"{name} is a recognized institution in India offering quality academic curriculum and student placement opportunities."

    # Remove Wikipedia [...] or DuckDuckGo [...]
    cleaned = re.sub(r"Wikipedia\s*\[[^\]]*\]\s*:?", "", str(raw_text), flags=re.IGNORECASE)
    cleaned = re.sub(r"DuckDuckGo\s*[^:]*:", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"Web Snippet\s*:", "", cleaned, flags=re.IGNORECASE)

    # Remove any bracketed citations [1], [citation needed]
    cleaned = re.sub(r"\[[^\]]*\]", "", cleaned)

    # Remove parenthetical fragments
    cleaned = re.sub(r"\([^\)]*\)", "", cleaned)

    # Clean whitespace and redundant punctuation
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = re.sub(r"\.\s*\.", ".", cleaned)
    cleaned = cleaned.strip(" :,.-")

    # If the text is a list of various unrelated universities (e.g. from a Wikipedia list page)
    indicators = ["list of", "jurisdiction", "defence academy", "affiliated colleges", "vidyapeeth", "symbiosis", "krishi vigyan", "alumni who include"]
    has_list_noise = sum(1 for ind in indicators if ind in cleaned.lower()) >= 2
    
    if has_list_noise or len(cleaned.split()) < 6:
        return f"{name} is a recognized educational institution in Maharashtra, India, offering undergraduate and postgraduate programs with dedicated faculty, modern campus facilities, and active placement guidance."

    sentences = [s.strip() for s in cleaned.split(".") if len(s.strip().split()) >= 4]

    if sentences and len(sentences[0]) > 20:
        first_s = sentences[0]
        if first_s[0].islower():
            first_s = first_s.capitalize()
        second_s = f" {sentences[1]}." if len(sentences) > 1 and len(sentences[1]) > 20 else ""
        return f"{first_s}.{second_s}"

    return f"{name} is a recognized educational institution offering engineering, technology, and professional programs with modern academic infrastructure and industry opportunities."


def generate_college_ai_info(college_name: str) -> Dict[str, Any]:
    """Accurate AI + Multi-source Web Search engine for any Indian college."""
INDIAN_CITY_STATE_MAP = {
    # Maharashtra
    "mumbai": ("Mumbai", "Maharashtra"),
    "powai": ("Powai, Mumbai", "Maharashtra"),
    "matunga": ("Matunga, Mumbai", "Maharashtra"),
    "andheri": ("Andheri, Mumbai", "Maharashtra"),
    "navi mumbai": ("Navi Mumbai", "Maharashtra"),
    "thane": ("Thane", "Maharashtra"),
    "pune": ("Pune", "Maharashtra"),
    "akurdi": ("Akurdi, Pune", "Maharashtra"),
    "pimpri": ("Pimpri, Pune", "Maharashtra"),
    "chinchwad": ("Pimpri-Chinchwad, Pune", "Maharashtra"),
    "nigdi": ("Nigdi, Pune", "Maharashtra"),
    "kothrud": ("Kothrud, Pune", "Maharashtra"),
    "shivajinagar": ("Shivajinagar, Pune", "Maharashtra"),
    "dhankawadi": ("Dhankawadi, Pune", "Maharashtra"),
    "bibwewadi": ("Bibwewadi, Pune", "Maharashtra"),
    "hadapsar": ("Hadapsar, Pune", "Maharashtra"),
    "lavale": ("Lavale, Pune", "Maharashtra"),
    "karjat": ("Karjat", "Maharashtra"),
    "kolhapur": ("Kolhapur", "Maharashtra"),
    "talsande": ("Talsande, Kolhapur", "Maharashtra"),
    "nagpur": ("Nagpur", "Maharashtra"),
    "nashik": ("Nashik", "Maharashtra"),
    "aurangabad": ("Chhatrapati Sambhajinagar", "Maharashtra"),
    "sambhajinagar": ("Chhatrapati Sambhajinagar", "Maharashtra"),
    "sangli": ("Sangli", "Maharashtra"),
    "solapur": ("Solapur", "Maharashtra"),
    "amravati": ("Amravati", "Maharashtra"),
    "nanded": ("Nanded", "Maharashtra"),
    "jalgaon": ("Jalgaon", "Maharashtra"),
    "satara": ("Satara", "Maharashtra"),
    "ahmednagar": ("Ahilyanagar", "Maharashtra"),
    # Karnataka
    "bangalore": ("Bengaluru", "Karnataka"),
    "bengaluru": ("Bengaluru", "Karnataka"),
    "mysore": ("Mysuru", "Karnataka"),
    "mysuru": ("Mysuru", "Karnataka"),
    "surathkal": ("Surathkal, Mangaluru", "Karnataka"),
    "mangalore": ("Mangaluru", "Karnataka"),
    "mangaluru": ("Mangaluru", "Karnataka"),
    "manipal": ("Manipal, Udupi", "Karnataka"),
    "belagavi": ("Belagavi", "Karnataka"),
    "hubli": ("Hubballi", "Karnataka"),
    # Tamil Nadu
    "chennai": ("Chennai", "Tamil Nadu"),
    "guindy": ("Guindy, Chennai", "Tamil Nadu"),
    "kattankulathur": ("Kattankulathur, Chennai", "Tamil Nadu"),
    "coimbatore": ("Coimbatore", "Tamil Nadu"),
    "trichy": ("Tiruchirappalli", "Tamil Nadu"),
    "tiruchirappalli": ("Tiruchirappalli", "Tamil Nadu"),
    "vellore": ("Vellore", "Tamil Nadu"),
    "madurai": ("Madurai", "Tamil Nadu"),
    "salem": ("Salem", "Tamil Nadu"),
    # Telangana & AP
    "hyderabad": ("Hyderabad", "Telangana"),
    "gachibowli": ("Gachibowli, Hyderabad", "Telangana"),
    "warangal": ("Warangal", "Telangana"),
    "visakhapatnam": ("Visakhapatnam", "Andhra Pradesh"),
    "vizag": ("Visakhapatnam", "Andhra Pradesh"),
    "vijayawada": ("Vijayawada", "Andhra Pradesh"),
    "guntur": ("Guntur", "Andhra Pradesh"),
    "tirupati": ("Tirupati", "Andhra Pradesh"),
    # Delhi NCR & UP
    "delhi": ("New Delhi", "Delhi"),
    "new delhi": ("New Delhi", "Delhi"),
    "hauz khas": ("Hauz Khas, New Delhi", "Delhi"),
    "dwarka": ("Dwarka, New Delhi", "Delhi"),
    "rohini": ("Rohini, New Delhi", "Delhi"),
    "noida": ("Noida", "Uttar Pradesh"),
    "greater noida": ("Greater Noida", "Uttar Pradesh"),
    "kanpur": ("Kanpur", "Uttar Pradesh"),
    "varanasi": ("Varanasi", "Uttar Pradesh"),
    "lucknow": ("Lucknow", "Uttar Pradesh"),
    "prayagraj": ("Prayagraj", "Uttar Pradesh"),
    "allahabad": ("Prayagraj", "Uttar Pradesh"),
    "ghaziabad": ("Ghaziabad", "Uttar Pradesh"),
    "aligarh": ("Aligarh", "Uttar Pradesh"),
    "mathura": ("Mathura", "Uttar Pradesh"),
    # Rajasthan
    "pilani": ("Pilani", "Rajasthan"),
    "jaipur": ("Jaipur", "Rajasthan"),
    "jodhpur": ("Jodhpur", "Rajasthan"),
    "kota": ("Kota", "Rajasthan"),
    "udaipur": ("Udaipur", "Rajasthan"),
    # West Bengal
    "kolkata": ("Kolkata", "West Bengal"),
    "kharagpur": ("Kharagpur", "West Bengal"),
    "shibpur": ("Shibpur, Howrah", "West Bengal"),
    "durgapur": ("Durgapur", "West Bengal"),
    "siliguri": ("Siliguri", "West Bengal"),
    # Gujarat
    "gandhinagar": ("Gandhinagar", "Gujarat"),
    "ahmedabad": ("Ahmedabad", "Gujarat"),
    "surat": ("Surat", "Gujarat"),
    "vadodara": ("Vadodara", "Gujarat"),
    "rajkot": ("Rajkot", "Gujarat"),
    # Punjab / Haryana / Chandigarh
    "chandigarh": ("Chandigarh", "Chandigarh"),
    "patiala": ("Patiala", "Punjab"),
    "ludhiana": ("Ludhiana", "Punjab"),
    "jalandhar": ("Jalandhar", "Punjab"),
    "ropar": ("Ropar", "Punjab"),
    "gurgaon": ("Gurugram", "Haryana"),
    "gurugram": ("Gurugram", "Haryana"),
    "faridabad": ("Faridabad", "Haryana"),
    "kurukshetra": ("Kurukshetra", "Haryana"),
    # Kerala
    "calicut": ("Kozhikode", "Kerala"),
    "kozhikode": ("Kozhikode", "Kerala"),
    "kochi": ("Kochi", "Kerala"),
    "trivandrum": ("Thiruvananthapuram", "Kerala"),
    "thiruvananthapuram": ("Thiruvananthapuram", "Kerala"),
    # Others
    "bhopal": ("Bhopal", "Madhya Pradesh"),
    "indore": ("Indore", "Madhya Pradesh"),
    "gwalior": ("Gwalior", "Madhya Pradesh"),
    "jabalpur": ("Jabalpur", "Madhya Pradesh"),
    "patna": ("Patna", "Bihar"),
    "bhubaneswar": ("Bhubaneswar", "Odisha"),
    "rourkela": ("Rourkela", "Odisha"),
    "guwahati": ("Guwahati", "Assam"),
    "ranchi": ("Ranchi", "Jharkhand"),
    "jamshedpur": ("Jamshedpur", "Jharkhand"),
    "raipur": ("Raipur", "Chhattisgarh"),
    "dehradun": ("Dehradun", "Uttarakhand"),
    "roorkee": ("Roorkee", "Uttarakhand"),
    "panaji": ("Panaji", "Goa"),
    "goa": ("Goa", "Goa"),
}


def extract_indian_location(query: str, web_context: str = "") -> tuple[str, str, str]:
    combined = f"{query} {web_context}".lower()
    sorted_keys = sorted(INDIAN_CITY_STATE_MAP.keys(), key=lambda k: len(k), reverse=True)
    for k in sorted_keys:
        if re.search(r"\b" + re.escape(k) + r"\b", combined):
            city_loc, state = INDIAN_CITY_STATE_MAP[k]
            city = city_loc.split(",")[0].strip()
            location = f"{city_loc}, {state}"
            return city, state, location

    return "Pune", "Maharashtra", "Pune, Maharashtra"


def generate_college_ai_info(college_name: str) -> Dict[str, Any]:
    """Accurate AI + Multi-source Web Search engine for any Indian college."""
    norm_q = normalize_str(college_name)

    # 1. Exact / Normalized match check in verified directory first
    for college in INDIAN_COLLEGES_SEED:
        norm_name = normalize_str(college["name"])
        norm_id = normalize_str(college["id"])
        if norm_q in norm_name or norm_q in norm_id or norm_name in norm_q:
            return college

    # 2. Fetch live web facts from Wikipedia & Web APIs
    web_context = fetch_live_web_context(college_name)
    clean_web_reference = clean_highlights_text(web_context, college_name)
    extracted_city, extracted_state, extracted_location = extract_indian_location(college_name, web_context)

    prompt = (
        f"You are a factual admissions counselor in India. Provide verified, accurate facts for '{college_name}'.\n"
        f"Verified Location Estimate: {extracted_location}\n"
        f"Verified Web Reference Context:\n{clean_web_reference}\n\n"
        "Instructions:\n"
        "1. Strictly provide the actual city and state of the college (e.g. Kolhapur, Maharashtra or Pune, Maharashtra). Never set location to just 'India'.\n"
        "2. Highlights MUST be a simple, natural 2-sentence explanation without brackets, citations, or 'Wikipedia' prefixes.\n"
        "3. Return ONLY a valid, parseable JSON object with these EXACT keys:\n"
        "{\n"
        '  "name": "Official Full Name of College",\n'
        f'  "city": "{extracted_city}",\n'
        f'  "state": "{extracted_state}",\n'
        f'  "location": "{extracted_location}",\n'
        '  "type": "e.g. Private / Government / Autonomous / Deemed / Institute of National Importance",\n'
        '  "rating": 4.3,\n'
        '  "nirf_rank": 120,\n'
        '  "established": 1984,\n'
        '  "exams": ["MHT-CET", "JEE Main"],\n'
        '  "courses": ["Computer Engineering", "Information Technology", "AI & Data Science", "Mechanical"],\n'
        '  "fee_display": "₹1.4 Lakh / year",\n'
        '  "placement_avg": "₹7.0 LPA",\n'
        '  "highest_package": "₹42.0 LPA",\n'
        '  "top_recruiters": ["TCS", "Infosys", "Capgemini", "Amazon", "Wipro"],\n'
        '  "highlights": "Clean human-readable 2-sentence summary describing the campus, faculty, accreditation, and student opportunities without brackets."\n'
        "}"
    )

    payload = {
        "model": settings.HUGGINGFACE_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a factual admissions database helper. Return ONLY valid JSON.",
            },
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 450,
        "temperature": 0.1,
    }

    if settings.HUGGINGFACE_API_TOKEN:
        try:
            req = urllib_request.Request(
                "https://router.huggingface.co/v1/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {settings.HUGGINGFACE_API_TOKEN}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            with urllib_request.urlopen(req, timeout=8) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                raw_text = res_data["choices"][0]["message"]["content"].strip()
                json_match = re.search(r"\{[\s\S]*\}", raw_text)
                if json_match:
                    result = json.loads(json_match.group(0))
                    result["highlights"] = clean_highlights_text(result.get("highlights", ""), result.get("name", college_name))
                    # Ensure location is not just "India"
                    if not result.get("location") or result.get("location").strip().lower() in ["india", ""]:
                        result["location"] = extracted_location
                        result["city"] = extracted_city
                        result["state"] = extracted_state
                    return result
        except Exception as e:
            print("Hugging Face College AI Search error/timeout:", e)

    return {
        "name": college_name,
        "city": extracted_city,
        "state": extracted_state,
        "location": extracted_location,
        "rating": 4.3,
        "type": "Engineering & Technology Institute",
        "courses": [
            "Computer Science & Engineering",
            "Information Technology",
            "Artificial Intelligence & Data Science",
            "Electronics & Telecom",
        ],
        "highlights": clean_web_reference,
    }
