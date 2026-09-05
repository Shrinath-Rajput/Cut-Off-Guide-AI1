export const EXAM_CONFIG = {
  'MHT-CET': {
    min: 0,
    max: 200,
    type: 'marks',
    label: 'MHT-CET Marks (Max 200)',
    description: 'Physics (50) + Chemistry (50) + Mathematics (100) = 200 Marks',
    courses: [
      'Computer Engineering (CSE)',
      'Information Technology (IT)',
      'Artificial Intelligence & Machine Learning',
      'Artificial Intelligence & Data Science',
      'Cyber Security',
      'Data Science',
      'Electronics & Telecommunication',
      'Electronics & Communication',
      'Electrical Engineering',
      'Mechanical Engineering',
      'Civil Engineering',
      'Chemical Engineering',
      'Robotics & Automation',
      'Mechatronics',
      'Biotechnology',
      'Aerospace Engineering',
      'Automobile Engineering',
      'Others',
    ],
  },
  'JEE Main': {
    min: 0,
    max: 300,
    type: 'marks',
    label: 'JEE Main Score (Max 300)',
    description: 'Physics (100) + Chemistry (100) + Mathematics (100) = 300 Marks',
    courses: [
      'Computer Engineering (CSE)',
      'Information Technology (IT)',
      'Artificial Intelligence & Machine Learning',
      'Artificial Intelligence & Data Science',
      'Cyber Security',
      'Data Science',
      'Electronics & Telecommunication',
      'Electronics & Communication',
      'Electrical Engineering',
      'Mechanical Engineering',
      'Civil Engineering',
      'Chemical Engineering',
      'Robotics & Automation',
      'Mechatronics',
      'Biotechnology',
      'Aerospace Engineering',
      'Automobile Engineering',
      'Others',
    ],
  },
  'JEE Advanced': {
    min: 0,
    max: 360,
    type: 'marks',
    label: 'JEE Advanced Score (Max 360)',
    description: 'Paper 1 (180) + Paper 2 (180) = 360 Total Marks',
    courses: [
      'Computer Engineering (CSE)',
      'Information Technology (IT)',
      'Artificial Intelligence & Machine Learning',
      'Artificial Intelligence & Data Science',
      'Cyber Security',
      'Data Science',
      'Electronics & Telecommunication',
      'Electronics & Communication',
      'Electrical Engineering',
      'Mechanical Engineering',
      'Civil Engineering',
      'Chemical Engineering',
      'Robotics & Automation',
      'Mechatronics',
      'Biotechnology',
      'Aerospace Engineering',
      'Automobile Engineering',
      'Others',
    ],
  },
  'NEET': {
    min: -720,
    max: 720,
    type: 'marks',
    label: 'NEET Score',
    courses: ['MBBS', 'BDS', 'BAMS', 'BHMS'],
  },
  'B.Pharm CET': {
    min: 0,
    max: 100,
    type: 'percentile',
    label: 'B.Pharm CET Percentile',
    courses: ['B.Pharm'],
  },
  'D.Pharm CET': {
    min: 0,
    max: 100,
    type: 'percentile',
    label: 'D.Pharm CET Percentile',
    courses: ['D.Pharm'],
  },
  'Diploma': {
    min: 0,
    max: 100,
    type: 'percentage',
    label: 'Diploma Percentage',
    courses: ['Mechanical', 'Civil', 'Computer', 'Electrical'],
  },
};

export const validateAcademicScore = (exam, score) => {
  if (!exam || score === '' || score === null || score === undefined) return null;
  const num = parseFloat(score);
  if (isNaN(num)) return 'Score must be a valid number';
  const config = EXAM_CONFIG[exam];
  if (config) {
    if (num < config.min) {
      return `${exam} score cannot be less than ${config.min}.`;
    }
    if (num > config.max) {
      return `${exam} maximum marks are ${config.max}. You entered ${num}.`;
    }
  }
  return null;
};
