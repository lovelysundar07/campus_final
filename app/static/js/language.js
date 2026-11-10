/**
 * MS College Campus Events - Bilingual Language Support
 * English / Tamil toggle with localStorage persistence
 */

const translations = {
  en: {
    // Navigation
    'nav.home':            'Home',
    'nav.events':          'Events',
    'nav.login':           'Login',
    'nav.register':        'Register',
    'nav.dashboard':       'Dashboard',
    'nav.logout':          'Logout',
    'nav.myRegistrations': 'My Registrations',
    'nav.certificates':    'Certificates',
    'nav.staffRegister':   'Staff Register',

    // Events
    'events.title':        'Campus Events',
    'events.workshop':     'Workshop',
    'events.seminar':      'Seminar',
    'events.symposium':    'Symposium',
    'events.register':     'Register Now',
    'events.upcoming':     'Upcoming',
    'events.ongoing':      'Ongoing',
    'events.completed':    'Completed',
    'events.date':         'Date',
    'events.time':         'Time',
    'events.venue':        'Venue',
    'events.capacity':     'Capacity',
    'events.deadline':     'Registration Deadline',
    'events.all':          'All Events',
    'events.noEvents':     'No events found',
    'events.filterAll':    'All',
    'events.spotsLeft':    'spots left',

    // Forms
    'form.name':           'Full Name',
    'form.rollNo':         'Roll Number',
    'form.dept':           'Department',
    'form.section':        'Section',
    'form.email':          'Email Address',
    'form.phone':          'Phone Number',
    'form.password':       'Password',
    'form.confirmPassword':'Confirm Password',
    'form.submit':         'Submit',
    'form.cancel':         'Cancel',
    'form.uploadPPT':      'Upload PPT/PDF',
    'form.teamName':       'Team Name',
    'form.addMember':      'Add Member',
    'form.designation':    'Designation',
    'form.description':    'Description',
    'form.startTime':      'Start Time',
    'form.endTime':        'End Time',
    'form.bannerImage':    'Banner Image',
    'form.regDeadline':    'Registration Deadline',

    // Auth
    'auth.login':              'Login',
    'auth.register':           'Create Account',
    'auth.forgotPassword':     'Forgot Password?',
    'auth.alreadyHaveAccount': 'Already have an account?',
    'auth.dontHaveAccount':    "Don't have an account?",
    'auth.signIn':             'Sign In',
    'auth.createAccount':      'Create Account',
    'auth.rememberMe':         'Remember me',
    'auth.staffRegister':      'Register as Staff',
    'auth.participantRegister':'Register as Participant',

    // Admin
    'admin.dashboard':        'Admin Dashboard',
    'admin.createEvent':      'Create Event',
    'admin.manageEvents':     'Manage Events',
    'admin.staffRequests':    'Staff Requests',
    'admin.issueCertificates':'Issue Certificates',
    'admin.reports':          'Reports',
    'admin.registrations':    'Registrations',
    'admin.totalEvents':      'Total Events',
    'admin.totalRegistrations':'Total Registrations',
    'admin.pendingRequests':  'Pending Requests',
    'admin.upcomingEvents':   'Upcoming Events',
    'admin.recentEvents':     'Recent Events',
    'admin.quickActions':     'Quick Actions',

    // Staff
    'staff.dashboard':        'Staff Dashboard',
    'staff.myEvents':         'My Events',
    'staff.reports':          'Reports',
    'staff.participants':     'Participants',
    'staff.attendance':       'Attendance',
    'staff.pptSubmissions':   'PPT Submissions',
    'staff.generateReport':   'Generate Report',
    'staff.markAttendance':   'Mark Attendance',

    // Participant
    'participant.dashboard':       'My Dashboard',
    'participant.registeredEvents':'Registered Events',
    'participant.certificates':    'My Certificates',
    'participant.pptsUploaded':    'PPTs Uploaded',
    'participant.browseEvents':    'Browse Events',
    'participant.welcome':         'Welcome back',
    'participant.downloadCert':    'Download Certificate',

    // Status
    'status.pending':   'Pending',
    'status.present':   'Present',
    'status.absent':    'Absent',
    'status.approved':  'Approved',
    'status.rejected':  'Rejected',
    'status.published': 'Published',
    'status.draft':     'Draft',
    'status.issued':    'Issued',

    // AI
    'ai.title':       'AI Assistant',
    'ai.placeholder': 'Ask me anything about events...',
    'ai.send':        'Send',
    'ai.thinking':    'Thinking...',
    'ai.clearChat':   'Clear chat',
    'ai.online':      'Online',

    // Messages
    'msg.success':             'Success!',
    'msg.error':               'Error!',
    'msg.loading':             'Loading...',
    'msg.noEvents':            'No events found',
    'msg.registrationSuccess': 'Successfully registered for the event!',
    'msg.certificateIssued':   'Certificate has been issued!',
    'msg.confirmDelete':       'Are you sure you want to delete this?',
    'msg.confirmApprove':      'Approve this staff request?',
    'msg.confirmReject':       'Reject this staff request?',

    // Symposium
    'symposium.selectSubEvent': 'Select Sub-event',
    'symposium.teamName':       'Team Name',
    'symposium.teamMembers':    'Team Members',
    'symposium.leader':         'Leader',
    'symposium.addMember':      'Add Member',
    'symposium.maxMembers':     'Maximum members reached',

    // Misc
    'misc.approve':       'Approve',
    'misc.reject':        'Reject',
    'misc.edit':          'Edit',
    'misc.delete':        'Delete',
    'misc.view':          'View',
    'misc.download':      'Download',
    'misc.publish':       'Publish',
    'misc.unpublish':     'Unpublish',
    'misc.assignStaff':   'Assign Staff',
    'misc.actions':       'Actions',
    'misc.search':        'Search...',
    'misc.filter':        'Filter',
    'misc.clear':         'Clear',
    'misc.back':          'Back',
    'misc.next':          'Next',
    'misc.previous':      'Previous',
    'misc.save':          'Save',
    'misc.close':         'Close',
    'misc.sNo':           'S.No',
    'misc.name':          'Name',
    'misc.type':          'Type',
    'misc.date':          'Date',
    'misc.status':        'Status',
    'misc.attendance':    'Attendance',
    'misc.certificate':   'Certificate',
  },

  ta: {
    // Navigation
    'nav.home':            'முகப்பு',
    'nav.events':          'நிகழ்வுகள்',
    'nav.login':           'உள்நுழைய',
    'nav.register':        'பதிவு செய்க',
    'nav.dashboard':       'டாஷ்போர்டு',
    'nav.logout':          'வெளியேறு',
    'nav.myRegistrations': 'என் பதிவுகள்',
    'nav.certificates':    'சான்றிதழ்கள்',
    'nav.staffRegister':   'ஊழியர் பதிவு',

    // Events
    'events.title':        'வளாக நிகழ்வுகள்',
    'events.workshop':     'பயிலரங்கு',
    'events.seminar':      'கருத்தரங்கு',
    'events.symposium':    'சிம்போசியம்',
    'events.register':     'இப்போதே பதிவு செய்க',
    'events.upcoming':     'வரவிருக்கும்',
    'events.ongoing':      'நடந்துகொண்டிருக்கும்',
    'events.completed':    'முடிந்தது',
    'events.date':         'தேதி',
    'events.time':         'நேரம்',
    'events.venue':        'இடம்',
    'events.capacity':     'இடங்கள்',
    'events.deadline':     'பதிவு கடைசி தேதி',
    'events.all':          'அனைத்து நிகழ்வுகள்',
    'events.noEvents':     'நிகழ்வுகள் இல்லை',
    'events.filterAll':    'அனைத்தும்',
    'events.spotsLeft':    'இடங்கள் உள்ளன',

    // Forms
    'form.name':           'முழு பெயர்',
    'form.rollNo':         'சுருள் எண்',
    'form.dept':           'துறை',
    'form.section':        'பிரிவு',
    'form.email':          'மின்னஞ்சல்',
    'form.phone':          'தொலைபேசி எண்',
    'form.password':       'கடவுச்சொல்',
    'form.confirmPassword':'கடவுச்சொல் உறுதிப்படுத்துக',
    'form.submit':         'சமர்ப்பிக்க',
    'form.cancel':         'ரத்து செய்',
    'form.uploadPPT':      'PPT/PDF பதிவேற்றவும்',
    'form.teamName':       'அணி பெயர்',
    'form.addMember':      'உறுப்பினரை சேர்க்க',
    'form.designation':    'பதவி',
    'form.description':    'விளக்கம்',
    'form.startTime':      'தொடக்க நேரம்',
    'form.endTime':        'முடிவு நேரம்',
    'form.bannerImage':    'பேனர் படம்',
    'form.regDeadline':    'பதிவு கடைசி நாள்',

    // Auth
    'auth.login':              'உள்நுழைய',
    'auth.register':           'கணக்கை உருவாக்கு',
    'auth.forgotPassword':     'கடவுச்சொல் மறந்தீர்களா?',
    'auth.alreadyHaveAccount': 'ஏற்கனவே கணக்கு உள்ளதா?',
    'auth.dontHaveAccount':    'கணக்கு இல்லையா?',
    'auth.signIn':             'உள்நுழைய',
    'auth.createAccount':      'கணக்கை உருவாக்கு',
    'auth.rememberMe':         'என்னை நினைவில் வைத்திரு',
    'auth.staffRegister':      'ஊழியராக பதிவு செய்க',
    'auth.participantRegister':'பங்கேற்பாளராக பதிவு செய்க',

    // Admin
    'admin.dashboard':         'நிர்வாக டாஷ்போர்டு',
    'admin.createEvent':       'நிகழ்வை உருவாக்கு',
    'admin.manageEvents':      'நிகழ்வுகளை நிர்வகி',
    'admin.staffRequests':     'ஊழியர் கோரிக்கைகள்',
    'admin.issueCertificates': 'சான்றிதழ்கள் வழங்கு',
    'admin.reports':           'அறிக்கைகள்',
    'admin.registrations':     'பதிவுகள்',
    'admin.totalEvents':       'மொத்த நிகழ்வுகள்',
    'admin.totalRegistrations':'மொத்த பதிவுகள்',
    'admin.pendingRequests':   'நிலுவையில் உள்ள கோரிக்கைகள்',
    'admin.upcomingEvents':    'வரவிருக்கும் நிகழ்வுகள்',
    'admin.recentEvents':      'சமீபத்திய நிகழ்வுகள்',
    'admin.quickActions':      'விரைவு செயல்கள்',

    // Staff
    'staff.dashboard':       'ஊழியர் டாஷ்போர்டு',
    'staff.myEvents':        'என் நிகழ்வுகள்',
    'staff.reports':         'அறிக்கைகள்',
    'staff.participants':    'பங்கேற்பாளர்கள்',
    'staff.attendance':      'வருகை',
    'staff.pptSubmissions':  'PPT சமர்ப்பிப்புகள்',
    'staff.generateReport':  'அறிக்கை உருவாக்கு',
    'staff.markAttendance':  'வருகை குறி',

    // Participant
    'participant.dashboard':        'என் டாஷ்போர்டு',
    'participant.registeredEvents': 'பதிவு செய்த நிகழ்வுகள்',
    'participant.certificates':     'என் சான்றிதழ்கள்',
    'participant.pptsUploaded':     'PPT பதிவேற்றங்கள்',
    'participant.browseEvents':     'நிகழ்வுகளை உலாவு',
    'participant.welcome':          'மீண்டும் வரவேற்கிறோம்',
    'participant.downloadCert':     'சான்றிதழ் பதிவிறக்கம்',

    // Status
    'status.pending':   'நிலுவையில்',
    'status.present':   'வந்தனர்',
    'status.absent':    'வரவில்லை',
    'status.approved':  'அங்கீகரிக்கப்பட்டது',
    'status.rejected':  'நிராகரிக்கப்பட்டது',
    'status.published': 'வெளியிடப்பட்டது',
    'status.draft':     'வரைவு',
    'status.issued':    'வழங்கப்பட்டது',

    // AI
    'ai.title':       'AI உதவியாளர்',
    'ai.placeholder': 'நிகழ்வுகள் பற்றி கேளுங்கள்...',
    'ai.send':        'அனுப்பு',
    'ai.thinking':    'யோசிக்கிறேன்...',
    'ai.clearChat':   'அரட்டையை அழி',
    'ai.online':      'ஆன்லைன்',

    // Messages
    'msg.success':             'வெற்றி!',
    'msg.error':               'பிழை!',
    'msg.loading':             'ஏற்றுகிறது...',
    'msg.noEvents':            'நிகழ்வுகள் இல்லை',
    'msg.registrationSuccess': 'நிகழ்வில் வெற்றிகரமாக பதிவு செய்யப்பட்டது!',
    'msg.certificateIssued':   'சான்றிதழ் வழங்கப்பட்டது!',
    'msg.confirmDelete':       'இதை நீக்க நிச்சயமாக விரும்புகிறீர்களா?',
    'msg.confirmApprove':      'இந்த ஊழியர் கோரிக்கையை அங்கீகரிக்கவா?',
    'msg.confirmReject':       'இந்த ஊழியர் கோரிக்கையை நிராகரிக்கவா?',

    // Symposium
    'symposium.selectSubEvent': 'துணை நிகழ்வை தேர்ந்தெடுக்கவும்',
    'symposium.teamName':       'அணி பெயர்',
    'symposium.teamMembers':    'அணி உறுப்பினர்கள்',
    'symposium.leader':         'தலைவர்',
    'symposium.addMember':      'உறுப்பினரை சேர்க்க',
    'symposium.maxMembers':     'அதிகபட்ச உறுப்பினர்கள் எட்டப்பட்டனர்',

    // Misc
    'misc.approve':       'அங்கீகரி',
    'misc.reject':        'நிராகரி',
    'misc.edit':          'திருத்து',
    'misc.delete':        'நீக்கு',
    'misc.view':          'காண்க',
    'misc.download':      'பதிவிறக்கம்',
    'misc.publish':       'வெளியிடு',
    'misc.unpublish':     'திரும்பப் பெறு',
    'misc.assignStaff':   'ஊழியர் நியமி',
    'misc.actions':       'செயல்கள்',
    'misc.search':        'தேடுக...',
    'misc.filter':        'வடிகட்டு',
    'misc.clear':         'அழி',
    'misc.back':          'திரும்பு',
    'misc.next':          'அடுத்து',
    'misc.previous':      'முந்தைய',
    'misc.save':          'சேமி',
    'misc.close':         'மூடு',
    'misc.sNo':           'வ.எண்',
    'misc.name':          'பெயர்',
    'misc.type':          'வகை',
    'misc.date':          'தேதி',
    'misc.status':        'நிலை',
    'misc.attendance':    'வருகை',
    'misc.certificate':   'சான்றிதழ்',
  }
};

// ── Language Manager Class ──
class LanguageManager {
  constructor() {
    this.currentLang = localStorage.getItem('campus_lang') || 'en';
    this.listeners   = [];
    this.init();
  }

  init() {
    this.applyLanguage(this.currentLang);

    document.querySelectorAll('.lang-toggle').forEach(btn => {
      btn.addEventListener('click', () => this.toggle());
    });
  }

  toggle() {
    this.currentLang = this.currentLang === 'en' ? 'ta' : 'en';
    localStorage.setItem('campus_lang', this.currentLang);
    this.applyLanguage(this.currentLang);
    this.listeners.forEach(fn => fn(this.currentLang));
  }

  applyLanguage(lang) {
    const dict = translations[lang] || translations['en'];

    // Text content
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (dict[key] !== undefined) {
        el.textContent = dict[key];
      }
    });

    // Placeholder
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      const key = el.getAttribute('data-i18n-placeholder');
      if (dict[key] !== undefined) {
        el.placeholder = dict[key];
      }
    });

    // Title attribute
    document.querySelectorAll('[data-i18n-title]').forEach(el => {
      const key = el.getAttribute('data-i18n-title');
      if (dict[key] !== undefined) {
        el.title = dict[key];
      }
    });

    // Aria-label attribute
    document.querySelectorAll('[data-i18n-aria]').forEach(el => {
      const key = el.getAttribute('data-i18n-aria');
      if (dict[key] !== undefined) {
        el.setAttribute('aria-label', dict[key]);
      }
    });

    // Toggle button label
    document.querySelectorAll('.lang-toggle').forEach(btn => {
      btn.textContent = lang === 'en' ? '🌐 தமிழ்' : '🌐 English';
    });

    // Document lang attribute
    document.documentElement.setAttribute('lang', lang === 'ta' ? 'ta' : 'en');

    // Dispatch custom event
    document.dispatchEvent(new CustomEvent('languageChanged', { detail: { lang } }));
  }

  /**
   * Translate a key to the current language.
   * Falls back to English, then to the key itself.
   */
  t(key) {
    const dict = translations[this.currentLang];
    if (dict && dict[key] !== undefined) return dict[key];
    if (translations['en'][key] !== undefined) return translations['en'][key];
    return key;
  }

  /**
   * Register a callback for language changes.
   */
  onChange(fn) {
    this.listeners.push(fn);
  }

  /**
   * Get current language code.
   */
  get lang() {
    return this.currentLang;
  }
}

// Instantiate globally
const langManager = new LanguageManager();

// Export for use in other scripts
window.langManager  = langManager;
window.translations = translations;
