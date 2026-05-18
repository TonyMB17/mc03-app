import axios from 'axios';

export const AUTH_TOKEN_KEY = 'neoabancay_auth_token';
export const AUTH_USER_KEY = 'neoabancay_auth_user';

const api = axios.create();

export function setAuthToken(token) {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`;
    localStorage.setItem(AUTH_TOKEN_KEY, token);
    return;
  }

  delete api.defaults.headers.common.Authorization;
  localStorage.removeItem(AUTH_TOKEN_KEY);
}

export function saveAuthUser(user) {
  if (user) {
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
    return;
  }
  localStorage.removeItem(AUTH_USER_KEY);
}

export function loadStoredAuth() {
  const token = localStorage.getItem(AUTH_TOKEN_KEY);
  const rawUser = localStorage.getItem(AUTH_USER_KEY);
  let user = null;
  if (rawUser) {
    try {
      user = JSON.parse(rawUser);
    } catch {
      user = null;
    }
  }
  if (token) setAuthToken(token);
  return { token, user };
}

export function clearAuth() {
  setAuthToken(null);
  saveAuthUser(null);
}

export default api;
