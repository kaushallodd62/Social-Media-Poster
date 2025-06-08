import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import RegisterPage from './page';
import { AuthProvider } from '../../contexts/AuthContext';
import React from 'react';

// Mock useRouter
jest.mock('next/navigation', () => ({
  useRouter: () => ({ push: jest.fn() }),
}));

// Mock useAuth
const registerMock = jest.fn();
const googleLoginMock = jest.fn();
jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({
    register: registerMock,
    googleLogin: googleLoginMock,
  }),
}));

function renderRegister() {
  return render(
    <AuthProvider>
      <RegisterPage />
    </AuthProvider>
  );
}

describe('RegisterPage', () => {
  beforeEach(() => {
    registerMock.mockReset();
    googleLoginMock.mockReset();
  });

  it('renders all fields and buttons', () => {
    renderRegister();
    expect(screen.getByLabelText(/display name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument();
    expect(screen.getByText(/sign up with google/i)).toBeInTheDocument();
  });

  it('shows validation errors for empty fields', async () => {
    renderRegister();
    fireEvent.click(screen.getByRole('button', { name: /create account/i }));
    expect(await screen.findByText(/display name is required/i)).toBeInTheDocument();
    expect(await screen.findByText(/email is required/i)).toBeInTheDocument();
    expect(await screen.findByText(/password is required/i)).toBeInTheDocument();
  });

  it('shows error for invalid email', async () => {
    renderRegister();
    fireEvent.change(screen.getByLabelText(/display name/i), { target: { value: 'User' } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'invalid' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'Password1' } });
    fireEvent.click(screen.getByRole('button', { name: /create account/i }));
    expect(await screen.findByText(/email is invalid/i)).toBeInTheDocument();
  });

  it('shows error for weak password', async () => {
    renderRegister();
    fireEvent.change(screen.getByLabelText(/display name/i), { target: { value: 'User' } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'user@example.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'short' } });
    fireEvent.click(screen.getByRole('button', { name: /create account/i }));
    expect(await screen.findByText(/at least 8 characters/i)).toBeInTheDocument();
  });

  it('shows error for password missing requirements', async () => {
    renderRegister();
    fireEvent.change(screen.getByLabelText(/display name/i), { target: { value: 'User' } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'user@example.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'password' } });
    fireEvent.click(screen.getByRole('button', { name: /create account/i }));
    expect(await screen.findByText(/uppercase letter/i)).toBeInTheDocument();
  });

  it('calls register and handles success', async () => {
    registerMock.mockResolvedValueOnce(undefined);
    renderRegister();
    fireEvent.change(screen.getByLabelText(/display name/i), { target: { value: 'User' } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'user@example.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'Password1' } });
    fireEvent.click(screen.getByRole('button', { name: /create account/i }));
    await waitFor(() => expect(registerMock).toHaveBeenCalledWith('user@example.com', 'Password1', 'User'));
  });

  it('shows error on register failure', async () => {
    registerMock.mockRejectedValueOnce(new Error('Email already exists'));
    renderRegister();
    fireEvent.change(screen.getByLabelText(/display name/i), { target: { value: 'User' } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'user@example.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'Password1' } });
    fireEvent.click(screen.getByRole('button', { name: /create account/i }));
    expect(await screen.findByText(/email already exists/i)).toBeInTheDocument();
  });

  it('calls googleLogin on Google button click', async () => {
    googleLoginMock.mockResolvedValueOnce(undefined);
    renderRegister();
    fireEvent.click(screen.getByText(/sign up with google/i));
    await waitFor(() => expect(googleLoginMock).toHaveBeenCalled());
  });
}); 