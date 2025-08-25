import streamlit as st
import re
import time
import random
import pandas as pd
from datetime import datetime, date, timedelta
import urllib.parse
import json
import os
from pathlib import Path

# Configure the page
st.set_page_config(
    page_title="LGL HR Portal",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS styling with improved formatting
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, rgb(52, 152, 219) 0%, rgb(41, 128, 185) 100%) !important;
        padding: 2rem;
        border-radius: 15px;
        color: white !important;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
    }
    
    .main-header h1 {
        color: white !important;
        font-size: 2.5rem !important;
        margin: 0 !important;
    }
    
    .main-header p {
        color: white !important;
        opacity: 0.9 !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, rgb(52, 152, 219) 0%, rgb(41, 128, 185) 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 12px !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        height: 70px !important;
        box-shadow: 0 3px 10px rgba(52, 152, 219, 0.3) !important;
        transition: all 0.3s ease !important;
        text-align: center !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, rgb(41, 128, 185) 0%, rgb(31, 78, 121) 100%) !important;
        color: white !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4) !important;
    }
    
    .bot-message {
        background: rgb(248, 249, 250) !important;
        padding: 1.5rem !important;
        border-radius: 12px !important;
        border-left: 4px solid rgb(52, 152, 219) !important;
        margin: 1rem 0 !important;
        color: rgb(44, 62, 80) !important;
        box-shadow: 0 2px 8px rgba(52, 152, 219, 0.1) !important;
        line-height: 1.6 !important;
    }
    
    .bot-message h2, .bot-message h3 {
        color: rgb(52, 152, 219) !important;
        margin-top: 1rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    .bot-message ul {
        margin: 0.5rem 0 !important;
        padding-left: 1.5rem !important;
    }
    
    .bot-message li {
        margin-bottom: 0.3rem !important;
    }
    
    .user-message {
        background: linear-gradient(135deg, rgb(52, 152, 219), rgb(41, 128, 185)) !important;
        color: white !important;
        padding: 1.5rem !important;
        border-radius: 12px !important;
        margin: 1rem 0 !important;
        text-align: right !important;
    }
    
    .footer {
        background-color: rgb(248, 249, 250);
        padding: 2rem;
        border-radius: 15px;
        margin-top: 3rem;
        text-align: center;
        border: 1px solid rgb(226, 232, 240);
    }
    
    .form-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
        border: 1px solid #e3e6f0;
    }
    
    .form-header {
        background: linear-gradient(135deg, rgb(52, 152, 219) 0%, rgb(41, 128, 185) 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    .form-header h3 {
        color: white !important;
        margin: 0 !important;
        font-size: 1.4rem !important;
    }
    
    .success-message {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 10px;
        color: #155724;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .info-box {
        background: #f8f9fa;
        border-left: 4px solid rgb(52, 152, 219);
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Employee Database - Sample Data for Leave Tracking
EMPLOYEE_DATA = {
    'john_doe': {
        'name': 'John Doe',
        'department': 'Academic Staff',
        'approval_manager': 'HR Manager',
        'employee_id': 'EMP001',
        'join_date': '2023-01-15',
        'contract_type': 'Unlimited',
        'position': 'English Teacher',
        'email': 'john.doe@lgl.com',
        'phone': '+971-50-123-4567',
        'annual_leave_taken': 8,
        'sick_leave_taken': 2,
        'maternity_leave_taken': 0,
        'parental_leave_taken': 0,
        'bereavement_leave_taken': 0,
        'probation_completed': True,
        'years_of_service': 1.8
    },
    'sarah_smith': {
        'name': 'Sarah Smith',
        'department': 'Administration',
        'approval_manager': 'HR Manager',
        'employee_id': 'EMP002',
        'join_date': '2022-08-10',
        'contract_type': 'Unlimited',
        'position': 'Administrative Assistant',
        'email': 'sarah.smith@lgl.com',
        'phone': '+971-50-234-5678',
        'annual_leave_taken': 12,
        'sick_leave_taken': 3,
        'maternity_leave_taken': 0,
        'parental_leave_taken': 0,
        'bereavement_leave_taken': 0,
        'probation_completed': True,
        'years_of_service': 2.3
    },
    'ahmed_hassan': {
        'name': 'Ahmed Hassan',
        'department': 'Academic Staff',
        'approval_manager': 'Academic Director',
        'employee_id': 'EMP003',
        'join_date': '2024-01-20',
        'contract_type': 'Limited',
        'position': 'Academic Coordinator',
        'email': 'ahmed.hassan@lgl.com',
        'phone': '+971-50-345-6789',
        'annual_leave_taken': 5,
        'sick_leave_taken': 1,
        'maternity_leave_taken': 0,
        'parental_leave_taken': 0,
        'bereavement_leave_taken': 0,
        'probation_completed': True,
        'years_of_service': 0.7
    }
}

# Comprehensive LGL Handbook Data
HANDBOOK_DATA = {
    'working_hours': {
        'title': '🕒 Working Hours',
        'content': """
**👨‍💼 Administrative Staff:**
• 📅 **Working Days:** Monday – Friday
• ⏰ **Working Hours:** 9:00am – 6:00pm

**👨‍🏫 Academic Staff:**
• 📚 **Minimum:** 2 teaching sessions per day
• 🕘 **Morning Session:** 9:00am-12:00pm
• 🕐 **Afternoon Session:** 12:00pm-3:00pm
• 🕕 **Evening Session:** 3:00pm-6:00pm
• 📅 **Working Days:** Monday to Friday

**⏰ Overtime Policy:**
• 💰 **Payment:** According to confirmed attendance
• 👔 **Approval:** At management's discretion
• 📝 **Documentation:** Proper time tracking required

**🌙 Ramadan Hours:**
• ⏳ **Reduction:** 2 hours less per day for administrative staff
• 📢 **Notice:** One week advance notice for revised working times
• 🕌 **Respect:** Accommodating religious observances
        """,
        'keywords': ['working hours', 'schedule', 'time', 'overtime', 'ramadan', 'shift', 'administrative', 'academic']
    },
    'annual_leave': {
        'title': '🏖️ Annual Leave Policy',
        'content': """
**📅 Annual Leave Entitlement:**
• 🎆 **First Year:** 20 working days (after probation completion)
• 🎉 **Subsequent Years:** 22 working days annually
• ⏰ **Notice Required:** Minimum twice the duration requested
• 🔄 **Example:** 2 weeks notice for 1 week leave

**📝 Application Process:**
• 📎 **Step 1:** Submit Annual Leave Form to line manager
• 🏃‍♂️ **Priority:** First-come, first-served basis
• 🔍 **Review:** Subject to operational requirements
• ✅ **Approval:** Manager confirmation required

**📦 Carrying Over Leave:**
• 👨‍💼 **Administrative Staff:** Maximum 7 days carry-over
• 👨‍🏫 **Teaching Staff:** Cannot carry over leave
• 🗺️ **Planning:** Use annual allocation within the year

**🌴 Peak Periods Restrictions:**
• 🚫 **Limited Availability:** July and August restrictions
• 📢 **Advance Notice:** 4 weeks notice for restricted periods
• 📈 **Priority:** Critical business operations first
        """,
        'keywords': ['annual leave', 'vacation', 'holiday', 'time off', 'leave policy', 'probation']
    },
    'sick_leave': {
        'title': '🏥 Sick Leave Policy',
        'content': """
**📅 Sick Leave Entitlement:**
• 🔢 **Total Allocation:** 90 calendar days per year
• ✅ **Eligibility:** After 3 months post-probation
• 💰 **Full Pay:** First 15 days
• 💸 **Half Pay:** Next 30 days (days 16-45)
• ❌ **No Pay:** Final 45 days (days 46-90)

**📝 Application Process:**
• 📢 **Immediate Notification Required:**
  • 👨‍🏫 **Academic Staff:** Within 1.5 hours
  • 👨‍💼 **Administrative Staff:** Within 1 hour
• 🏥 **Medical Certificate:** Required after 2 days absence
• 📎 **Sick Leave Form:** Complete upon return to work
• 📞 **Contact:** Notify both line manager and HR

**🌡️ Coverage Includes:**
• 🤒 **Illness Recovery:** General health conditions
• ⚙️ **Medical Procedures:** Surgery and treatments
• 🏅 **Severe Injury Recovery:** Accident-related injuries
• 😷 **COVID-19:** Quarantine and isolation periods
• 👩‍⚕️ **Doctor Appointments:** Essential medical visits
        """,
        'keywords': ['sick leave', 'illness', 'medical', 'health', 'doctor', 'certificate', 'absence']
    },
    'maternity_leave': {
        'title': '👶 Maternity & Parental Leave',
        'content': """
**🤰 Maternity Leave Entitlement:**
• 📅 **Total Duration:** 60 days maternity leave
• 💰 **Full Pay:** First 45 consecutive calendar days
• 💸 **Half Pay:** Following 15 days
• 📢 **Advance Notice:** 15 weeks before due date
• 📝 **Documentation:** Written notice required

**⏳ Extended Maternity Leave:**
• 📅 **Additional Time:** 100 days without pay
• 🔄 **Flexibility:** Consecutive or non-consecutive days
• 🏥 **Medical Extensions:** Certificate required for illness-related extensions
• 👩‍⚕️ **Health Priority:** Mother's wellbeing considered

**👨‍👩‍👶 Parental Leave Benefits:**
• 👩 **Female Employees:** Additional 5 days within 6 months of birth
• 👨 **Male Employees:** 5 days within 6 months of birth
• 👪 **Family Bonding:** Encouraging parental involvement
• 💰 **Paid Leave:** Full compensation during parental leave

**🍼 Feeding Breaks Policy:**
• ⏰ **Duration:** Two 30-minute breaks daily
• 📅 **Period:** Available for 18 months post-delivery
• 💼 **Work Integration:** Considered part of working hours
• 👶 **Child Care:** Supporting nursing mothers
        """,
        'keywords': ['maternity leave', 'parental leave', 'pregnancy', 'birth', 'feeding breaks', 'family']
    },
    'bereavement_leave': {
        'title': '🕊 Bereavement / Compassionate Leave',
        'content': """
**📅 Bereavement Leave Entitlement:**
• 💑 **Spouse Death:** Five (5) paid days
• 👪 **Immediate Family Death:** Three (3) paid days
  • 👨‍👩‍👧‍👦 **Includes:** Parent, child, sibling, grandchild, grandparent
• 💰 **Compensation:** Full pay during leave period

**📢 Application Process:**
• ⏰ **Immediate Notification:** Contact reporting line manager ASAP
• 📅 **Latest Notification:** First day of absence
• 🎆 **Exceptional Circumstances:** Applications considered after first day
• 👔 **Management Discretion:** Case-by-case evaluation
• 📝 **Documentation:** Death certificate may be required

**🤝 Support Available:**
• 💬 **Regular Check-ins:** Progress discussions with line manager
• 🔒 **Confidential Support:** HR Manager discussions about grief impact
• 🏠 **Return Assistance:** Work performance support during transition
• 👪 **Family Care:** Time off for dependent emergencies

**🛡️ Coverage Summary:**
• 💑 **Spouse Loss:** 5 paid days
• 👨‍👩‍👧 **Immediate Family Loss:** 3 paid days
• 🏠 **Emergency Dependent Care:** Reasonable unpaid leave
• 💓 **Emotional Support:** Counseling resources available
        """,
        'keywords': ['bereavement', 'compassionate', 'death', 'family', 'grief', 'emergency', 'dependent']
    },
    'code_of_conduct': {
        'title': '📋 Code of Conduct',
        'content': """
**🎆 Employee Duties & Responsibilities:**
• 🎨 **Professional Excellence:** Exercise reasonable skill and care
• 📜 **Policy Compliance:** Obey rules, policies, and work directions
• 🏢 **Property Care:** Maintain company property and facilities
• 🔒 **Confidentiality:** Protect trade secrets and sensitive information
• 🤝 **Good Faith:** Act with integrity and maintain trust
• 🎆 **Accountability:** Take responsibility for actions and decisions

**👕 Professional Dress Code:**
• ✨ **Standard:** Smart, professional attire required
• ❌ **Prohibited Items:**
  • 👔 Torn, dirty, or inappropriate clothing
  • 👀 Transparent clothing or low necklines
  • 🩳 Shorts or flip-flops
• 🎨 **Body Art:** Tattoos and piercings should be covered where possible
• 👑 **Professional Image:** Maintain company reputation

**🛡️ Safeguarding Standards:**
• 🚫 **Physical Contact:** No physical contact with students
• 👥 **Supervision:** Avoid being alone with students
• 📏 **Boundaries:** Maintain professional relationships
• ❌ **Personal Relationships:** No personal relationships with students
• 📢 **Reporting:** Report safeguarding concerns immediately
• 👶 **Child Protection:** Prioritize student safety and wellbeing
        """,
        'keywords': ['conduct', 'dress code', 'safeguarding', 'professional', 'behavior', 'standards']
    },
    'disciplinary_procedures': {
        'title': '⚖️ Disciplinary Procedures',
        'content': """
**🟡 Minor Misconduct Examples:**
• ⏰ **Attendance Issues:** Persistent lateness and poor timekeeping
• 🚫 **Unauthorized Absence:** Absence without valid reason
• 📋 **Procedure Violations:** Failure to follow prescribed procedures
• 📉 **Performance Issues:** Incompetence or failure to meet standards
• 📞 **Communication:** Poor response to guidance and feedback

**🔴 Gross Misconduct Examples:**
• 🔒 **Theft:** Unauthorized possession of company property
• 🍷 **Substance Abuse:** Being unfit for duty due to alcohol/drug use
• 🥊 **Violence:** Physical assault or verbal abuse
• 📢 **Confidentiality Breach:** Sharing sensitive information
• ⚠️ **Discrimination:** Unlawful discrimination or harassment
• 🚫 **Serious Violations:** Actions that damage company reputation

**⏳ Warning Validity Periods:**
• 🗣️ **Verbal Warnings:** 6 months active period
• 📝 **First Written Warnings:** 12 months active period
• ⚠️ **Final Written Warnings:** 12 months active period
• 📅 **Record Keeping:** All warnings documented in personnel file

**📜 Appeal Rights Process:**
• ⏰ **Timeline:** 5 days to submit written appeal
• 📅 **Meeting:** Appeal meeting within 20 working days
• 👔 **Review:** Independent management review
• ⚖️ **Fair Process:** Right to representation and fair hearing
        """,
        'keywords': ['disciplinary', 'misconduct', 'warnings', 'dismissal', 'appeals', 'procedures']
    },
    'performance_management': {
        'title': '🎆 Performance Management',
        'content': """
**📅 Performance Appraisal Schedule:**
• 🎆 **Initial Review:** First appraisal after 6-month probation
• 🔄 **Annual Reviews:** Formal reviews conducted yearly
• 📈 **Mid-Year Reviews:** Optional 6-month progress check-ins
• ⏰ **Timing:** Scheduled based on hire date anniversary

**📊 Appraisal Components:**
• 🏆 **Achievement Review:** Assessment of previous year's accomplishments
• 🎨 **Development Planning:** Personal Development Plan for coming year
• 📚 **Training Identification:** Skills and training needs assessment
• 🚀 **Career Discussions:** Future career planning and growth opportunities
• 📈 **Goal Setting:** SMART objectives for the upcoming period

**⏳ Probationary Period Management:**
• 📅 **Duration:** 6 months for all new staff members
• 🔍 **Continuous Monitoring:** Performance tracking throughout probation
• 💬 **Review Meeting:** Formal assessment at completion
• ⏳ **Extension Option:** Possible 3-month extension if needed
• ✅ **Confirmation:** Permanent employment confirmation upon success

**🎆 Key Management Principles:**
• ⚖️ **Fair Process:** Equitable treatment for all employees
• 🔒 **Confidentiality:** Private and secure discussions
• 💬 **Two-Way Communication:** Open dialogue and feedback
• 🚀 **Development Focus:** Emphasis on growth and improvement
• 🏅 **Recognition:** Acknowledging achievements and progress
        """,
        'keywords': ['performance', 'appraisal', 'review', 'probation', 'development', 'evaluation']
    },
    'termination_gratuity': {
        'title': '🏁 Termination & Gratuity',
        'content': """
**📅 Notice Periods Required:**
• ♾️ **Unlimited Contracts:** 30 calendar days minimum notice
• 📆 **Limited Contracts:** No notice required at natural expiry
• 📝 **Written Notice:** Formal documentation required
• ⏰ **Mutual Agreement:** Terms can be negotiated between parties

**💰 Gratuity Calculation Structure:**
• 🎆 **Years 1-5:** 21 calendar days' basic pay per year of service
• 🚀 **Year 6+:** 30 calendar days' basic pay per year of service
• 🔢 **Maximum Cap:** Total not exceeding 2 years' pay equivalent
• 📈 **Calculation Base:** Based on final basic salary

**📋 Limited Contract Resignation Rules:**
• ❌ **Under 5 Years Service:** No gratuity entitlement
• ✅ **Over 5 Years Service:** Same calculation as unlimited contracts
• 📅 **Service Period:** Continuous employment counted
• 💼 **Contract Type:** Rules apply based on final contract status

**⚠️ Early Termination Compensation:**
• 🏢 **Employer Termination:** 3 months' remuneration minimum
• 👨‍💼 **Employee Termination:** Half of 3 months' remuneration
• ⚖️ **Legal Compliance:** As per UAE Labor Law
• 💸 **Payment Timeline:** Settlement within 14 days

**📝 Exit Process Requirements:**
• 💬 **Exit Interview:** Conducted with HR department
• 🖼️ **Property Return:** All company assets and equipment
• 💳 **Final Settlement:** Complete financial reconciliation
• 📋 **Documentation:** Clearance certificates and references
        """,
        'keywords': ['termination', 'resignation', 'gratuity', 'notice period', 'compensation', 'exit']
    }
}

# Calculate leave entitlements
def calculate_leave_entitlements(employee_data):
    years_of_service = employee_data['years_of_service']
    annual_entitlement = 22 if years_of_service >= 1 else 20
    
    return {
        'annual_leave': {
            'entitlement': annual_entitlement,
            'taken': employee_data['annual_leave_taken'],
            'remaining': annual_entitlement - employee_data['annual_leave_taken']
        },
        'sick_leave': {
            'entitlement': 90,
            'taken': employee_data['sick_leave_taken'],
            'remaining': 90 - employee_data['sick_leave_taken']
        }
    }

# Form submission handler
def save_form_submission(form_type, form_data):
    """Save form submission to JSON file"""
    submissions_dir = Path("submissions")
    submissions_dir.mkdir(exist_ok=True)
    
    filename = f"{form_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = submissions_dir / filename
    
    with open(filepath, 'w') as f:
        json.dump(form_data, f, indent=2, default=str)
    
    return filename

def process_user_query(query):
    """Process user query and return appropriate response with smart leave detection"""
    query_lower = query.lower()
    
    # Smart leave type detection - show options when user types general terms
    leave_triggers = ['leave', 'time off', 'absence', 'vacation', 'holiday']
    if any(trigger in query_lower for trigger in leave_triggers) and not any(specific in query_lower for specific in ['annual', 'sick', 'maternity', 'parental', 'bereavement']):
        return {
            'type': 'leave_options',
            'content': "🏖️ **Which type of leave are you asking about?**\n\nPlease select from the options below:"
        }
    
    # Leave balance queries
    if any(word in query_lower for word in ['balance', 'remaining', 'left', 'how many']):
        if st.session_state.get('current_employee'):
            emp_data = st.session_state.employee_data
            leave_data = calculate_leave_entitlements(emp_data)
            return {
                'type': 'text',
                'content': f"""
**📊 Your Current Leave Balances:**

**🏖️ Annual Leave:**
• 🎆 **Remaining:** {leave_data['annual_leave']['remaining']} days
• 💰 **Total Entitlement:** {leave_data['annual_leave']['entitlement']} days
• 📋 **Already Used:** {leave_data['annual_leave']['taken']} days

**🏥 Sick Leave:**
• 🎆 **Remaining:** {leave_data['sick_leave']['remaining']} days
• 💰 **Total Entitlement:** {leave_data['sick_leave']['entitlement']} days
• 📋 **Already Used:** {leave_data['sick_leave']['taken']} days

💡 **Need to apply for leave?** Ask me "How do I apply for annual leave?" for the complete application process!
"""
            }
        else:
            return {
                'type': 'text',
                'content': "Please select your employee profile from the sidebar to view your leave balances."
            }
    
    # Specific policy queries
    if any(word in query_lower for word in ['apply', 'application', 'request', 'form']):
        if any(word in query_lower for word in ['leave', 'vacation', 'holiday']):
            return {
                'type': 'text',
                'content': """
**📝 How to Apply for Leave - Step by Step Guide:**

**🚀 Application Process:**
• **📅 Step 1:** Submit Annual Leave Form to your line manager
• **⏰ Step 2:** Provide minimum notice (twice the duration requested)
• **✅ Step 3:** Wait for approval based on operational requirements

**📊 Timing Examples:**
• 🏖️ **1 Week Leave:** Submit request 2 weeks in advance
• 🏴 **2 Week Leave:** Submit request 4 weeks in advance
• 🎆 **3 Week Leave:** Submit request 6 weeks in advance

**⚠️ Important Restrictions:**
• 🏴 **Peak Season:** Limited availability during July-August
• 📢 **Advance Notice:** 4 weeks notice given for restricted periods
• 🏃‍♂️ **Priority System:** First-come, first-served basis

**📞 Need Help?**
• 📎 **Forms:** Contact HR Department for leave forms
• 👨‍💼 **Questions:** Speak with your line manager
• 💬 **Policy Details:** Ask me about specific leave policies
"""
            }
    
    # Find best matching topic
    best_match = None
    best_score = 0
    
    for topic_key, topic_data in HANDBOOK_DATA.items():
        score = 0
        for keyword in topic_data['keywords']:
            if keyword in query_lower:
                score += 1
        
        if score > best_score:
            best_score = score
            best_match = topic_data
    
    if best_match:
        return {
            'type': 'text',
            'content': f"**{best_match['title']}**\n{best_match['content']}"
        }
    
    return {
        'type': 'text',
        'content': """
🚀 **Welcome to LGL HR Assistant!** I'm here to help with all your HR policy questions! 🎆

**📚 Available Topics:**

• 🕒 **Working Hours** - Schedule, overtime, Ramadan hours
• 🏖️ **Annual Leave** - Entitlements, application process  
• 🏥 **Sick Leave** - Medical leave policies
• 👶 **Maternity/Parental Leave** - Family leave policies
• 📋 **Code of Conduct** - Professional standards, dress code
• 🎆 **Performance Management** - Appraisals and reviews
• ⚖️ **Disciplinary Procedures** - Warnings, misconduct, appeals
• 🏁 **Termination & Gratuity** - Notice periods, end-of-service benefits

**⚡ Quick Commands:**
• 📊 "My leave balance" - Check your remaining days
• 📝 "How do I apply for leave?" - Application process
• 👕 "What is the dress code?" - Professional standards
• ⚖️ "Disciplinary procedure" - Misconduct and warnings

**🎁 Pro Tip:**
💬 **Try typing:** "leave" to see all leave options with clickable buttons!
"""
    }

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'show_leave_options' not in st.session_state:
    st.session_state.show_leave_options = False
if 'current_employee' not in st.session_state:
    st.session_state.current_employee = None
if 'employee_data' not in st.session_state:
    st.session_state.employee_data = None
if 'app_mode' not in st.session_state:
    st.session_state.app_mode = 'HR Assistant'

# Sidebar Navigation
st.sidebar.title("🏢 LGL HR Portal")
st.sidebar.markdown("---")

# Navigation buttons
nav_options = ["🤖 HR Assistant", "📝 Employee Forms"]
app_mode = st.sidebar.radio("Select Mode:", nav_options, index=0)

# Update app mode
if app_mode == "🤖 HR Assistant":
    st.session_state.app_mode = "HR Assistant"
elif app_mode == "📝 Employee Forms":
    st.session_state.app_mode = "Employee Forms"

st.sidebar.markdown("---")

# Sidebar for employee selection (visible in all modes)
st.sidebar.title("👤 Employee Login")
employee_options = ['Select Employee'] + [emp_data['name'] for emp_data in EMPLOYEE_DATA.values()]
selected_employee = st.sidebar.selectbox("Choose your profile:", employee_options)

if selected_employee != 'Select Employee':
    # Find employee data
    employee_key = None
    for key, data in EMPLOYEE_DATA.items():
        if data['name'] == selected_employee:
            employee_key = key
            break
    
    if employee_key:
        st.session_state.current_employee = selected_employee
        st.session_state.employee_data = EMPLOYEE_DATA[employee_key]
        
        # Show employee info in sidebar
        emp_data = st.session_state.employee_data
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**👋 Welcome, {emp_data['name']}!**")
        st.sidebar.markdown(f"""
        **📋 Your Details:**
        • Department: {emp_data['department']}
        • Position: {emp_data['position']}
        • Employee ID: {emp_data['employee_id']}
        • Years of Service: {emp_data['years_of_service']} years
        """)
        
        # Quick leave balance
        leave_data = calculate_leave_entitlements(emp_data)
        st.sidebar.markdown(f"""
        **📅 Quick Leave Balance:**
        • Annual: {leave_data['annual_leave']['remaining']} days
        • Sick: {leave_data['sick_leave']['remaining']} days
        """)

# Main Application Logic
if st.session_state.app_mode == "HR Assistant":
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 LGL HR Assistant</h1>
        <p>Your intelligent guide to company policies and procedures</p>
    </div>
    """, unsafe_allow_html=True)

    # Content for HR Assistant mode

    # Main content area
    st.markdown("### 🚀 Quick Topics:")

    topic_cols = st.columns(3)
    with topic_cols[0]:
        if st.button("🕒 Working Hours"):
            response = process_user_query("working hours")
            st.session_state.messages.append({"role": "user", "content": "Working Hours"})
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

    with topic_cols[1]:
        if st.button("🏖️ Annual Leave"):
            response = process_user_query("annual leave")
            st.session_state.messages.append({"role": "user", "content": "Annual Leave"})
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

    with topic_cols[2]:
        if st.button("🏥 Sick Leave"):
            response = process_user_query("sick leave")
            st.session_state.messages.append({"role": "user", "content": "Sick Leave"})
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

    # Chat Interface
    st.markdown("---")
    st.markdown("### 💬 Ask me anything about HR policies:")

    # Display chat messages
    for i, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            # Handle different response types
            if isinstance(message["content"], dict):
                if message["content"]["type"] == "leave_options":
                    st.markdown(f'<div class="bot-message">{message["content"]["content"]}</div>', unsafe_allow_html=True)
                    
                    # Display leave type buttons
                    leave_cols = st.columns(2)
                    with leave_cols[0]:
                        if st.button("🏖️ Annual Leave", key=f"annual_{i}"):
                            response = process_user_query("annual leave")
                            st.session_state.messages.append({"role": "user", "content": "Annual Leave"})
                            st.session_state.messages.append({"role": "assistant", "content": response})
                            st.rerun()
                        
                        if st.button("👶 Maternity Leave", key=f"maternity_{i}"):
                            response = process_user_query("maternity leave")
                            st.session_state.messages.append({"role": "user", "content": "Maternity Leave"})
                            st.session_state.messages.append({"role": "assistant", "content": response})
                            st.rerun()
                    
                    with leave_cols[1]:
                        if st.button("🏥 Sick Leave", key=f"sick_{i}"):
                            response = process_user_query("sick leave")
                            st.session_state.messages.append({"role": "user", "content": "Sick Leave"})
                            st.session_state.messages.append({"role": "assistant", "content": response})
                            st.rerun()
                        
                        if st.button("🍼 Bereavement Leave", key=f"bereavement_{i}"):
                            response = process_user_query("bereavement leave")
                            st.session_state.messages.append({"role": "user", "content": "Bereavement Leave"})
                            st.session_state.messages.append({"role": "assistant", "content": response})
                            st.rerun()
                else:
                    st.markdown(f'<div class="bot-message">{message["content"]["content"]}</div>', unsafe_allow_html=True)
            else:
                # Handle string responses (backward compatibility)
                st.markdown(f'<div class="bot-message">{message["content"]}</div>', unsafe_allow_html=True)

    # Chat input
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Type your question here:", placeholder="e.g., leave, annual leave balance, or dress code")
        submitted = st.form_submit_button("Send")
        
        if submitted and user_input:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Generate response
            response = process_user_query(user_input)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            st.rerun()

    # Footer
    st.markdown("""
    <div class="footer">
        <strong>LGL HR Assistant</strong><br>
        Helping employees navigate company policies with ease<br>
        <small>Your intelligent guide to HR policies and procedures</small>
    </div>
    """, unsafe_allow_html=True)

# Employee Forms Section
elif st.session_state.app_mode == "Employee Forms":
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📝 LGL Employee Forms Portal</h1>
        <p>Submit your employment-related requests and applications</p>
    </div>
    """, unsafe_allow_html=True)

    # Main content
    if st.session_state.current_employee:
        emp_data = st.session_state.employee_data
        leave_data = calculate_leave_entitlements(emp_data)
        
        # Employee Entitlements Dashboard
        st.markdown("""
        <div class="form-container" style="margin-bottom: 2rem; background: linear-gradient(135deg, rgb(52, 152, 219) 0%, rgb(41, 128, 185) 100%); color: white;">
            <div class="form-header" style="background: transparent; color: white; margin-bottom: 1rem;">
                <h3 style="color: white !important; margin: 0;">👤 Employee Dashboard - {}</h3>
            </div>
        </div>
        """.format(emp_data['name']), unsafe_allow_html=True)
        
        # Entitlements Overview Cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="info-box" style="background: #e8f4fd; border-left: 4px solid #3498db; padding: 1rem; border-radius: 5px; text-align: center;">
                <h4 style="margin: 0; color: #2c3e50;">🏖️ Annual Leave</h4>
                <p style="margin: 0.5rem 0; font-size: 1.2rem; font-weight: bold; color: #3498db;">{} days</p>
                <small style="color: #7f8c8d;">Remaining / {} Total</small>
            </div>
            """.format(leave_data['annual_leave']['remaining'], leave_data['annual_leave']['entitlement']), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="info-box" style="background: #fdf2e9; border-left: 4px solid #e67e22; padding: 1rem; border-radius: 5px; text-align: center;">
                <h4 style="margin: 0; color: #2c3e50;">🏥 Sick Leave</h4>
                <p style="margin: 0.5rem 0; font-size: 1.2rem; font-weight: bold; color: #e67e22;">{} days</p>
                <small style="color: #7f8c8d;">Remaining / {} Total</small>
            </div>
            """.format(leave_data['sick_leave']['remaining'], leave_data['sick_leave']['entitlement']), unsafe_allow_html=True)
        
        with col3:
            years_service = emp_data['years_of_service']
            maternity_entitlement = "60 days" if years_service >= 0.25 else "Not Eligible"
            st.markdown("""
            <div class="info-box" style="background: #fdeaea; border-left: 4px solid #e74c3c; padding: 1rem; border-radius: 5px; text-align: center;">
                <h4 style="margin: 0; color: #2c3e50;">👶 Maternity</h4>
                <p style="margin: 0.5rem 0; font-size: 1.2rem; font-weight: bold; color: #e74c3c;">{}</p>
                <small style="color: #7f8c8d;">Paid Leave</small>
            </div>
            """.format(maternity_entitlement), unsafe_allow_html=True)
        
        with col4:
            bereavement_entitlement = "3-5 days" if years_service >= 0.25 else "Contact HR"
            st.markdown("""
            <div class="info-box" style="background: #f4f1fb; border-left: 4px solid #9b59b6; padding: 1rem; border-radius: 5px; text-align: center;">
                <h4 style="margin: 0; color: #2c3e50;">🕊️ Bereavement</h4>
                <p style="margin: 0.5rem 0; font-size: 1.2rem; font-weight: bold; color: #9b59b6;">{}</p>
                <small style="color: #7f8c8d;">Per Incident</small>
            </div>
            """.format(bereavement_entitlement), unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 🚀 Available Forms:")
        
        # Form selection
        form_options = [
            "Select a Form",
            "🏖️ Annual Leave Request",
            "🏥 Sick Leave Request", 
            "👶 Maternity/Parental Leave Request",
            "🕊️ Bereavement Leave Request",
            "📋 Resignation Letter",
            "⭐ Performance Review Request",
            "🎓 Training Request",
            "📢 Grievance/Complaint Form",
            "📱 Electronic Device Request",
            "🏭 Office Supplies Request",
            "🏠 Remote Work Request",
            "⏰ Overtime Authorization Request"
        ]
        
        selected_form = st.selectbox("Choose the form you need to submit:", form_options)
        
        emp_data = st.session_state.employee_data
        
        # Annual Leave Request Form
        if selected_form == "🏖️ Annual Leave Request":
            st.markdown('<div class="form-container">', unsafe_allow_html=True)
            st.markdown('<div class="form-header"><h3>🏖️ Annual Leave Request Form</h3></div>', unsafe_allow_html=True)
            
            with st.form("annual_leave_form"):
                st.markdown("**📝 Leave Details**")
                
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("Start Date", min_value=date.today() + timedelta(days=1))
                    leave_type = st.selectbox("Leave Type", ["Annual Leave", "Carry Over Leave"])
                    
                with col2:
                    end_date = st.date_input("End Date", min_value=start_date if 'start_date' in locals() else date.today())
                    # Auto-calculate total days based on date range
                    if start_date and end_date and end_date >= start_date:
                        total_days_calculated = (end_date - start_date).days + 1
                        st.info(f"📅 **Total Days:** {total_days_calculated} days (automatically calculated)")
                        total_days = total_days_calculated
                    else:
                        total_days = 1
                        st.warning("⚠️ Please select valid start and end dates")
                
                reason = st.text_area("Reason for Leave", placeholder="Briefly explain the purpose of your leave...")
                
                st.markdown("**📞 Emergency Contact**")
                col3, col4 = st.columns(2)
                with col3:
                    emergency_contact = st.text_input("Emergency Contact Name")
                with col4:
                    emergency_phone = st.text_input("Emergency Contact Phone")
                
                work_coverage = st.text_area("Work Coverage Arrangements", 
                                           placeholder="Describe how your work will be covered during your absence...")
                
                submitted = st.form_submit_button("Submit Annual Leave Request")
                
                if submitted:
                    if start_date and end_date and reason and emergency_contact:
                        leave_balance = calculate_leave_entitlements(emp_data)
                        
                        form_data = {
                            'form_type': 'Annual Leave Request',
                            'employee_name': emp_data['name'],
                            'employee_id': emp_data['employee_id'],
                            'department': emp_data['department'],
                            'submission_date': datetime.now().isoformat(),
                            'start_date': start_date.isoformat(),
                            'end_date': end_date.isoformat(),
                            'total_days': total_days,
                            'leave_type': leave_type,
                            'reason': reason,
                            'emergency_contact': emergency_contact,
                            'emergency_phone': emergency_phone,
                            'work_coverage': work_coverage,
                            'approval_manager': emp_data['approval_manager'],
                            'current_leave_balance': leave_balance['annual_leave']['remaining']
                        }
                        
                        filename = save_form_submission('annual_leave', form_data)
                        
                        st.markdown(f"""
                        <div class="success-message">
                            ✅ <strong>Annual Leave Request Submitted Successfully!</strong><br>
                            📄 Reference: {filename}<br>
                            📧 Your manager ({emp_data['approval_manager']}) has been notified.<br>
                            📅 Current Balance: {leave_balance['annual_leave']['remaining']} days remaining
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error("Please fill in all required fields")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Sick Leave Request Form
        elif selected_form == "🏥 Sick Leave Request":
            st.markdown('<div class="form-container">', unsafe_allow_html=True)
            st.markdown('<div class="form-header"><h3>🏥 Sick Leave Request Form</h3></div>', unsafe_allow_html=True)
            
            with st.form("sick_leave_form"):
                st.markdown("**🏥 Medical Leave Details**")
                
                col1, col2 = st.columns(2)
                with col1:
                    illness_start = st.date_input("Illness Start Date")
                    expected_return = st.date_input("Expected Return Date")
                    
                with col2:
                    leave_duration = st.number_input("Total Days", min_value=1, value=1)
                    medical_cert_required = st.checkbox("Medical Certificate Available (Required for 2+ days)")
                
                illness_type = st.selectbox("Type of Illness/Condition", 
                                          ["General Illness", "Injury", "Surgery", "Chronic Condition", 
                                           "COVID-19 Related", "Medical Procedure", "Other"])
                
                symptoms_description = st.text_area("Brief Description of Illness/Symptoms",
                                                  placeholder="Describe your condition (for medical records)...")
                
                st.markdown("**👨‍⚕️ Medical Information**")
                col3, col4 = st.columns(2)
                with col3:
                    doctor_name = st.text_input("Attending Doctor/Clinic Name")
                    doctor_contact = st.text_input("Doctor/Clinic Contact")
                with col4:
                    medical_cert_file = st.file_uploader("Upload Medical Certificate", 
                                                       type=['pdf', 'jpg', 'jpeg', 'png'])
                    follow_up_required = st.checkbox("Follow-up Medical Appointments Required")
                
                work_handover = st.text_area("Work Handover Notes",
                                           placeholder="Critical tasks that need immediate attention...")
                
                submitted = st.form_submit_button("Submit Sick Leave Request")
                
                if submitted:
                    if illness_start and expected_return and symptoms_description:
                        form_data = {
                            'form_type': 'Sick Leave Request',
                            'employee_name': emp_data['name'],
                            'employee_id': emp_data['employee_id'],
                            'department': emp_data['department'],
                            'submission_date': datetime.now().isoformat(),
                            'illness_start': illness_start.isoformat(),
                            'expected_return': expected_return.isoformat(),
                            'leave_duration': leave_duration,
                            'illness_type': illness_type,
                            'symptoms_description': symptoms_description,
                            'doctor_name': doctor_name,
                            'doctor_contact': doctor_contact,
                            'medical_cert_available': medical_cert_required,
                            'follow_up_required': follow_up_required,
                            'work_handover': work_handover,
                            'approval_manager': emp_data['approval_manager']
                        }
                        
                        filename = save_form_submission('sick_leave', form_data)
                        
                        st.markdown(f"""
                        <div class="success-message">
                            ✅ <strong>Sick Leave Request Submitted Successfully!</strong><br>
                            📄 Reference: {filename}<br>
                            📧 HR and your manager have been notified.<br>
                            💡 Remember to submit medical certificate if absence is 2+ days
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error("Please fill in all required fields")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Training Request Form
        elif selected_form == "🎓 Training Request":
            st.markdown('<div class="form-container">', unsafe_allow_html=True)
            st.markdown('<div class="form-header"><h3>🎓 Professional Training Request</h3></div>', unsafe_allow_html=True)
            
            with st.form("training_request_form"):
                st.markdown("**🎨 Training Details**")
                
                col1, col2 = st.columns(2)
                with col1:
                    training_title = st.text_input("Training Course/Program Title*")
                    training_provider = st.text_input("Training Provider/Institution")
                    training_type = st.selectbox("Training Type", 
                                                ["Online Course", "In-Person Workshop", "Certification Program", 
                                                 "Conference/Seminar", "Professional Development", "Skills Training"])
                    
                with col2:
                    training_start = st.date_input("Training Start Date", min_value=date.today())
                    training_end = st.date_input("Training End Date", min_value=training_start if 'training_start' in locals() else date.today())
                    estimated_cost = st.number_input("Estimated Cost (AED)", min_value=0, value=0, step=100)
                
                st.markdown("**🏆 Business Justification**")
                business_justification = st.text_area("How does this training benefit your role and the company?", 
                                                    placeholder="Explain the relevance, expected outcomes, and business impact...")
                
                col3, col4 = st.columns(2)
                with col3:
                    current_skill_level = st.selectbox("Current Skill Level in This Area", 
                                                      ["Beginner", "Intermediate", "Advanced", "Expert"])
                    priority_level = st.selectbox("Priority Level", ["High", "Medium", "Low"])
                    
                with col4:
                    expected_completion = st.date_input("Expected Completion Date")
                    certification_included = st.checkbox("Training includes professional certification")
                
                knowledge_sharing = st.text_area("Knowledge Sharing Plan", 
                                                placeholder="How will you share learned knowledge with your team?")
                
                additional_notes = st.text_area("Additional Notes (Optional)", 
                                               placeholder="Any additional information about the training...")
                
                submitted = st.form_submit_button("Submit Training Request")
                
                if submitted:
                    if training_title and business_justification and training_provider:
                        form_data = {
                            'form_type': 'Training Request',
                            'employee_name': emp_data['name'],
                            'employee_id': emp_data['employee_id'],
                            'department': emp_data['department'],
                            'submission_date': datetime.now().isoformat(),
                            'training_title': training_title,
                            'training_provider': training_provider,
                            'training_type': training_type,
                            'training_start': training_start.isoformat(),
                            'training_end': training_end.isoformat(),
                            'estimated_cost': estimated_cost,
                            'business_justification': business_justification,
                            'current_skill_level': current_skill_level,
                            'priority_level': priority_level,
                            'expected_completion': expected_completion.isoformat(),
                            'certification_included': certification_included,
                            'knowledge_sharing': knowledge_sharing,
                            'additional_notes': additional_notes,
                            'approval_manager': emp_data['approval_manager']
                        }
                        
                        filename = save_form_submission('training_request', form_data)
                        
                        st.markdown(f"""
                        <div class="success-message">
                            ✅ <strong>Training Request Submitted Successfully!</strong><br>
                            📄 Reference: {filename}<br>
                            📧 Your manager ({emp_data['approval_manager']}) will review your request.<br>
                            💰 Estimated Cost: AED {estimated_cost:,}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error("Please fill in all required fields (marked with *)")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
        # Performance Review Request Form
        elif selected_form == "⭐ Performance Review Request":
            st.markdown('<div class="form-container">', unsafe_allow_html=True)
            st.markdown('<div class="form-header"><h3>⭐ Performance Review Request</h3></div>', unsafe_allow_html=True)
            
            with st.form("performance_review_form"):
                st.markdown("**🔍 Review Details**")
                
                col1, col2 = st.columns(2)
                with col1:
                    review_type = st.selectbox("Review Type", 
                                             ["Mid-Year Review", "Annual Performance Review", "Probation Review", 
                                              "Project-Based Review", "Self-Assessment Update"])
                    review_reason = st.selectbox("Reason for Request", 
                                               ["Scheduled Review Due", "Performance Discussion", "Goal Reassessment", 
                                                "Career Development", "Feedback Request", "Other"])
                    
                with col2:
                    requested_date = st.date_input("Preferred Review Date", min_value=date.today())
                    review_urgency = st.selectbox("Urgency Level", ["Normal", "High", "Urgent"])
                
                st.markdown("**🏆 Current Performance Summary**")
                key_achievements = st.text_area("Key Achievements Since Last Review", 
                                              placeholder="Highlight your main accomplishments, completed projects, and contributions...")
                
                challenges_faced = st.text_area("Challenges Faced", 
                                               placeholder="Describe any obstacles or difficulties encountered...")
                
                st.markdown("**🚀 Development Goals**")
                col3, col4 = st.columns(2)
                with col3:
                    current_goals_status = st.text_area("Status of Current Goals", 
                                                      placeholder="Progress on existing objectives...")
                    
                with col4:
                    future_goals = st.text_area("Proposed Future Goals", 
                                               placeholder="Areas for development and growth...")
                
                feedback_360 = st.checkbox("🔄 Request 360-degree feedback (colleagues, subordinates)")
                career_discussion = st.checkbox("📋 Include career development discussion")
                
                additional_topics = st.text_area("Additional Discussion Topics", 
                                                placeholder="Any specific areas you'd like to discuss during the review...")
                
                submitted = st.form_submit_button("Submit Performance Review Request")
                
                if submitted:
                    if key_achievements and review_reason != "Other" or additional_topics:
                        form_data = {
                            'form_type': 'Performance Review Request',
                            'employee_name': emp_data['name'],
                            'employee_id': emp_data['employee_id'],
                            'department': emp_data['department'],
                            'submission_date': datetime.now().isoformat(),
                            'review_type': review_type,
                            'review_reason': review_reason,
                            'requested_date': requested_date.isoformat(),
                            'review_urgency': review_urgency,
                            'key_achievements': key_achievements,
                            'challenges_faced': challenges_faced,
                            'current_goals_status': current_goals_status,
                            'future_goals': future_goals,
                            'feedback_360': feedback_360,
                            'career_discussion': career_discussion,
                            'additional_topics': additional_topics,
                            'approval_manager': emp_data['approval_manager']
                        }
                        
                        filename = save_form_submission('performance_review', form_data)
                        
                        st.markdown(f"""
                        <div class="success-message">
                            ✅ <strong>Performance Review Request Submitted!</strong><br>
                            📄 Reference: {filename}<br>
                            📧 Your manager ({emp_data['approval_manager']}) will schedule your review.<br>
                            📅 Preferred Date: {requested_date.strftime('%B %d, %Y')}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error("Please provide key achievements and select appropriate reason")
            
                        
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Electronic Device Request Form
        elif selected_form == "📱 Electronic Device Request":
            st.markdown('<div class="form-container">', unsafe_allow_html=True)
            st.markdown('<div class="form-header"><h3>📱 Electronic Device Request</h3></div>', unsafe_allow_html=True)
            
            with st.form("electronic_device_form"):
                st.markdown("**💻 Device Details**")
                
                col1, col2 = st.columns(2)
                with col1:
                    device_type = st.selectbox("Device Type*", 
                                             ["Laptop/Computer", "Monitor", "Mobile Phone", "Tablet", 
                                              "Printer", "Webcam", "Headset", "Keyboard/Mouse", "Other"])
                    device_brand = st.text_input("Preferred Brand/Model")
                    urgency_level = st.selectbox("Urgency", ["Normal", "High", "Urgent"])
                    
                with col2:
                    required_date = st.date_input("Required By Date", min_value=date.today())
                    estimated_cost = st.number_input("Estimated Cost (AED)", min_value=0, value=0, step=100)
                    request_type = st.selectbox("Request Type", ["New Purchase", "Replacement", "Upgrade", "Temporary Use"])
                
                business_justification = st.text_area("Business Justification*", 
                                                     placeholder="Explain why this device is needed for your work...")
                
                col3, col4 = st.columns(2)
                with col3:
                    current_device_status = st.text_area("Current Device Status (if replacement)", 
                                                        placeholder="Describe issues with existing device...")
                    
                with col4:
                    technical_specs = st.text_area("Required Technical Specifications", 
                                                  placeholder="Specific requirements (RAM, storage, etc.)...")
                
                alternative_considered = st.text_area("Alternatives Considered", 
                                                     placeholder="Have you considered other options or workarounds?")
                
                submitted = st.form_submit_button("Submit Electronic Device Request")
                
                if submitted:
                    if device_type and business_justification:
                        form_data = {
                            'form_type': 'Electronic Device Request',
                            'employee_name': emp_data['name'],
                            'employee_id': emp_data['employee_id'],
                            'department': emp_data['department'],
                            'submission_date': datetime.now().isoformat(),
                            'device_type': device_type,
                            'device_brand': device_brand,
                            'urgency_level': urgency_level,
                            'required_date': required_date.isoformat(),
                            'estimated_cost': estimated_cost,
                            'request_type': request_type,
                            'business_justification': business_justification,
                            'current_device_status': current_device_status,
                            'technical_specs': technical_specs,
                            'alternative_considered': alternative_considered,
                            'approval_manager': emp_data['approval_manager']
                        }
                        
                        filename = save_form_submission('electronic_device', form_data)
                        
                        st.markdown(f"""
                        <div class="success-message">
                            ✅ <strong>Electronic Device Request Submitted!</strong><br>
                            📄 Reference: {filename}<br>
                            📧 IT Department and your manager have been notified.<br>
                            💰 Estimated Cost: AED {estimated_cost:,}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error("Please fill in all required fields (marked with *)")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Other Forms (Placeholder)
        elif selected_form in ["👶 Maternity/Parental Leave Request", "🕊️ Bereavement Leave Request", 
                              "📋 Resignation Letter", "📢 Grievance/Complaint Form",
                              "🏭 Office Supplies Request", "🏠 Remote Work Request", 
                              "⏰ Overtime Authorization Request"]:
            
            # Office Supplies Request Form
            if selected_form == "🏭 Office Supplies Request":
                st.markdown('<div class="form-container">', unsafe_allow_html=True)
                st.markdown('<div class="form-header"><h3>🏭 Office Supplies Request</h3></div>', unsafe_allow_html=True)
                
                with st.form("office_supplies_form"):
                    st.markdown("**📋 Supply Details**")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        supply_category = st.selectbox("Supply Category", 
                                                     ["Stationery", "Office Equipment", "Cleaning Supplies", 
                                                      "Furniture", "Software/Licenses", "Safety Equipment", "Other"])
                        urgency = st.selectbox("Urgency Level", ["Normal", "High", "Urgent"])
                        
                    with col2:
                        required_date = st.date_input("Required By Date", min_value=date.today())
                        total_budget = st.number_input("Estimated Total Cost (AED)", min_value=0, value=0, step=50)
                    
                    # Dynamic supply items list
                    st.markdown("**📦 Items Required**")
                    items_text = st.text_area("List of Items (one per line with quantity)", 
                                             placeholder="Example:\n- Pens (black ink) - 10 pieces\n- A4 Paper - 5 reams\n- Stapler - 1 piece")
                    
                    justification = st.text_area("Business Justification", 
                                                placeholder="Why are these supplies needed? Current stock status?")
                    
                    col3, col4 = st.columns(2)
                    with col3:
                        supplier_preference = st.text_input("Preferred Supplier (Optional)")
                        
                    with col4:
                        delivery_location = st.selectbox("Delivery Location", 
                                                       ["My Desk", "Reception", "Storage Room", "Department Office"])
                    
                    additional_notes = st.text_area("Additional Notes", 
                                                   placeholder="Special requirements, specifications, etc.")
                    
                    submitted = st.form_submit_button("Submit Office Supplies Request")
                    
                    if submitted and items_text and justification:
                        form_data = {
                            'form_type': 'Office Supplies Request',
                            'employee_name': emp_data['name'],
                            'employee_id': emp_data['employee_id'],
                            'department': emp_data['department'],
                            'submission_date': datetime.now().isoformat(),
                            'supply_category': supply_category,
                            'urgency': urgency,
                            'required_date': required_date.isoformat(),
                            'total_budget': total_budget,
                            'items_text': items_text,
                            'justification': justification,
                            'supplier_preference': supplier_preference,
                            'delivery_location': delivery_location,
                            'additional_notes': additional_notes,
                            'approval_manager': emp_data['approval_manager']
                        }
                        
                        filename = save_form_submission('office_supplies', form_data)
                        st.success(f"✅ Office Supplies Request submitted! Reference: {filename}")
                    elif submitted:
                        st.error("Please provide items list and justification")
                        
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Remote Work Request Form
            elif selected_form == "🏠 Remote Work Request":
                st.markdown('<div class="form-container">', unsafe_allow_html=True)
                st.markdown('<div class="form-header"><h3>🏠 Remote Work Request</h3></div>', unsafe_allow_html=True)
                
                with st.form("remote_work_form"):
                    st.markdown("**📅 Remote Work Details**")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        work_arrangement = st.selectbox("Work Arrangement Type", 
                                                       ["Permanent Remote", "Temporary Remote", "Hybrid (Part-time)", 
                                                        "Emergency Remote", "Project-Based Remote"])
                        start_date = st.date_input("Requested Start Date", min_value=date.today())
                        
                    with col2:
                        if work_arrangement != "Permanent Remote":
                            end_date = st.date_input("End Date (if temporary)", min_value=start_date)
                        work_days = st.multiselect("Remote Work Days (for hybrid)", 
                                                  ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
                    
                    reason_for_request = st.text_area("Reason for Remote Work Request", 
                                                     placeholder="Personal circumstances, project requirements, etc.")
                    
                    st.markdown("**💻 Work Setup & Productivity**")
                    home_office_setup = st.text_area("Home Office Setup Description", 
                                                    placeholder="Describe your workspace, equipment, internet connection...")
                    
                    productivity_plan = st.text_area("Productivity & Communication Plan", 
                                                    placeholder="How will you maintain productivity and team communication?")
                    
                    col3, col4 = st.columns(2)
                    with col3:
                        equipment_needed = st.checkbox("I need company equipment for remote work")
                        vpn_access = st.checkbox("I need VPN/system access setup")
                        
                    with col4:
                        client_meetings = st.checkbox("My role involves client meetings")
                        team_collaboration = st.selectbox("Team Collaboration Frequency", 
                                                        ["Daily", "Few times a week", "Weekly", "Monthly", "Minimal"])
                    
                    submitted = st.form_submit_button("Submit Remote Work Request")
                    
                    if submitted and reason_for_request and home_office_setup:
                        form_data = {
                            'form_type': 'Remote Work Request',
                            'employee_name': emp_data['name'],
                            'employee_id': emp_data['employee_id'],
                            'department': emp_data['department'],
                            'submission_date': datetime.now().isoformat(),
                            'work_arrangement': work_arrangement,
                            'start_date': start_date.isoformat(),
                            'end_date': end_date.isoformat() if work_arrangement != "Permanent Remote" and 'end_date' in locals() else None,
                            'work_days': work_days,
                            'reason_for_request': reason_for_request,
                            'home_office_setup': home_office_setup,
                            'productivity_plan': productivity_plan,
                            'equipment_needed': equipment_needed,
                            'vpn_access': vpn_access,
                            'client_meetings': client_meetings,
                            'team_collaboration': team_collaboration,
                            'approval_manager': emp_data['approval_manager']
                        }
                        
                        filename = save_form_submission('remote_work', form_data)
                        st.success(f"✅ Remote Work Request submitted! Reference: {filename}")
                    elif submitted:
                        st.error("Please provide reason and home office setup details")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Overtime Authorization Request Form  
            elif selected_form == "⏰ Overtime Authorization Request":
                st.markdown('<div class="form-container">', unsafe_allow_html=True)
                st.markdown('<div class="form-header"><h3>⏰ Overtime Authorization Request</h3></div>', unsafe_allow_html=True)
                
                with st.form("overtime_auth_form"):
                    st.markdown("**🕰️ Overtime Details**")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        overtime_date = st.date_input("Overtime Date", min_value=date.today())
                        start_time = st.time_input("Expected Start Time")
                        end_time = st.time_input("Expected End Time")
                        
                    with col2:
                        overtime_type = st.selectbox("Overtime Type", 
                                                   ["Regular Overtime", "Weekend Work", "Holiday Work", 
                                                    "Emergency Work", "Project Deadline"])
                        total_hours = st.number_input("Total Overtime Hours", min_value=0.5, max_value=12.0, step=0.5)
                        meal_allowance = st.checkbox("Meal allowance required")
                    
                    work_justification = st.text_area("Work Justification & Tasks", 
                                                     placeholder="Describe the work to be completed and why overtime is necessary...")
                    
                    col3, col4 = st.columns(2)
                    with col3:
                        project_code = st.text_input("Project/Department Code (if applicable)")
                        urgency_reason = st.text_area("Urgency Explanation", 
                                                    placeholder="Why can't this work be completed during regular hours?")
                        
                    with col4:
                        expected_outcome = st.text_area("Expected Deliverables", 
                                                       placeholder="What will be completed by the end of overtime?")
                        alternative_considered = st.text_area("Alternatives Considered", 
                                                            placeholder="Other options to avoid overtime?")
                    
                    submitted = st.form_submit_button("Submit Overtime Authorization Request")
                    
                    if submitted and work_justification and urgency_reason:
                        # Calculate estimated cost (example rate)
                        base_rate = 50  # AED per hour (example)
                        overtime_multiplier = 1.5
                        estimated_cost = total_hours * base_rate * overtime_multiplier
                        
                        form_data = {
                            'form_type': 'Overtime Authorization Request',
                            'employee_name': emp_data['name'],
                            'employee_id': emp_data['employee_id'],
                            'department': emp_data['department'],
                            'submission_date': datetime.now().isoformat(),
                            'overtime_date': overtime_date.isoformat(),
                            'start_time': start_time.strftime('%H:%M'),
                            'end_time': end_time.strftime('%H:%M'),
                            'overtime_type': overtime_type,
                            'total_hours': total_hours,
                            'meal_allowance': meal_allowance,
                            'work_justification': work_justification,
                            'project_code': project_code,
                            'urgency_reason': urgency_reason,
                            'expected_outcome': expected_outcome,
                            'alternative_considered': alternative_considered,
                            'estimated_cost': estimated_cost,
                            'approval_manager': emp_data['approval_manager']
                        }
                        
                        filename = save_form_submission('overtime_authorization', form_data)
                        
                        st.markdown(f"""
                        <div class="success-message">
                            ✅ <strong>Overtime Authorization Request Submitted!</strong><br>
                            📄 Reference: {filename}<br>
                            🕰️ Total Hours: {total_hours} hours<br>
                            💰 Estimated Cost: AED {estimated_cost:,.2f}
                        </div>
                        """, unsafe_allow_html=True)
                    elif submitted:
                        st.error("Please provide work justification and urgency explanation")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Basic forms for other types
            else:
                st.markdown('<div class="form-container">', unsafe_allow_html=True)
                st.markdown(f'<div class="form-header"><h3>{selected_form}</h3></div>', unsafe_allow_html=True)
                
                st.info(f"📝 {selected_form} form is being prepared. Please contact HR for immediate assistance.")
                
                # Quick contact form for urgent requests
                with st.form(f"{selected_form.lower().replace(' ', '_')}_quick_form"):
                    urgent_request = st.text_area("Urgent Request Description", 
                                                placeholder=f"Briefly describe your {selected_form.lower()} request...")
                    contact_preference = st.selectbox("Preferred Contact Method", ["Email", "Phone", "In-Person"])
                    
                    if st.form_submit_button(f"Submit {selected_form} Request"):
                        if urgent_request:
                            form_data = {
                                'form_type': selected_form,
                                'employee_name': emp_data['name'],
                                'employee_id': emp_data['employee_id'],
                                'department': emp_data['department'],
                                'submission_date': datetime.now().isoformat(),
                                'urgent_request': urgent_request,
                                'contact_preference': contact_preference,
                                'approval_manager': emp_data['approval_manager']
                            }
                            
                            filename = save_form_submission('urgent_request', form_data)
                            
                            st.success(f"✅ Urgent {selected_form} request submitted! Reference: {filename}")
                        else:
                            st.error("Please describe your request")
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        st.info("👤 Please log in as an employee to access the forms portal.")
        st.markdown("""
        ### 📋 Available Forms:
        - 🏖️ **Annual Leave Request** - Request time off for vacation
        - 🏥 **Sick Leave Request** - Apply for medical leave
        - 👶 **Maternity/Parental Leave** - Family leave applications
        - 🕊️ **Bereavement Leave** - Compassionate leave for loss
        - 📋 **Resignation Letter** - Formal resignation submission
        - ⭐ **Performance Review Request** - Request additional reviews
        - 🎓 **Training Request** - Professional development opportunities
        - 📢 **Grievance/Complaint** - Report workplace issues
        - 📱 **Electronic Device Request** - IT equipment requests
        - 🏭 **Office Supplies Request** - Stationery and office equipment
        - 🏠 **Remote Work Request** - Work from home arrangements
        - ⏰ **Overtime Authorization** - Pre-approve overtime work
        """)
    
    # Footer for Forms
    st.markdown("""
    <div class="footer">
        <strong>LGL Employee Forms Portal</strong><br>
        Streamlined employee request management<br>
        <small>All form submissions are securely stored and processed according to company policy</small>
    </div>
    """, unsafe_allow_html=True)