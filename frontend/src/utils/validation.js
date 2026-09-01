export const EXAM_CONFIG = {
  'JEE Main': { min: 0, max: 300, type: 'marks', label: 'JEE Main Score', courses: ['Computer Engineering', 'IT', 'ECE', 'Mechanical', 'Civil', 'Electrical', 'Chemical', 'AI & ML', 'Data Science'] },
  'JEE Advanced': { min: 0, max: 360, type: 'marks', label: 'JEE Advanced Score', courses: ['Computer Engineering', 'IT', 'ECE', 'Mechanical', 'Civil', 'Electrical', 'Chemical', 'AI & ML', 'Data Science'] },
  'MHT-CET': { min: 0, max: 100, type: 'percentile', label: 'MHT-CET Percentile', courses: ['Computer Engineering', 'IT', 'ECE', 'Mechanical', 'Civil', 'Electrical', 'Chemical', 'AI & ML', 'Data Science'] },
  'NEET': { min: -720, max: 720, type: 'marks', label: 'NEET Score', courses: ['MBBS', 'BDS', 'BAMS', 'BHMS'] },
  'B.Pharm CET': { min: 0, max: 100, type: 'percentile', label: 'B.Pharm CET Percentile', courses: ['B.Pharm'] },
  'D.Pharm CET': { min: 0, max: 100, type: 'percentile', label: 'D.Pharm CET Percentile', courses: ['D.Pharm'] },
  'Diploma': { min: 0, max: 100, type: 'percentage', label: 'Diploma Percentage', courses: ['Mechanical', 'Civil', 'Computer', 'Electrical'] },
  'GATE Commerce': { min: 0, max: 100, type: 'marks', label: 'GATE Commerce Score', courses: ['Commerce', 'Finance', 'Economics', 'Accounting', 'AI & ML', 'Data Science'] },
};

export const validateAcademicScore = (exam, score) => {
  if (!exam || !score) return null;
  const num = parseFloat(score);
  if (isNaN(num)) return 'Score must be a number';
  const config = EXAM_CONFIG[exam];
  if (config) {
    if (num < config.min || num > config.max) {
      return `${exam} ${config.type} must be between ${config.min} and ${config.max}.`;
    }
  }
  return null;
};
