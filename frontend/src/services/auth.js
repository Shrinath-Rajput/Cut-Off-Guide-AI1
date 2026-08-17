import { registerUser as registerUserApi } from './api';

export const registerUser = async (user) => {
  return registerUserApi(user);
};
