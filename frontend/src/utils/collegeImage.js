export const COLLEGE_PLACEHOLDER = '/college-placeholder.svg';

export const collegeImage = (image) => image || COLLEGE_PLACEHOLDER;

export const handleCollegeImageError = (event) => {
  if (event.currentTarget.src.endsWith(COLLEGE_PLACEHOLDER)) return;
  event.currentTarget.src = COLLEGE_PLACEHOLDER;
};