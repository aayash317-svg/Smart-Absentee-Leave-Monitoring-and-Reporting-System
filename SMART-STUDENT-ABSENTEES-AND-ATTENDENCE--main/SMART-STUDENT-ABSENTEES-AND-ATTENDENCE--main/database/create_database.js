// Create collections script for smart_absentee_db
db = db.getSiblingDB('smart_absentee_db');

const collections = [
  'users',
  'departments',
  'students',
  'absentees',
  'leaveApplications',
  'fineRules',
  'finePayments',
  'notifications',
  'auditLogs',
  'reports'
];

collections.forEach(col => {
  if (!db.getCollectionNames().includes(col)) {
    db.createCollection(col);
    print(`Created collection: ${col}`);
  } else {
    print(`Collection already exists: ${col}`);
  }
});
