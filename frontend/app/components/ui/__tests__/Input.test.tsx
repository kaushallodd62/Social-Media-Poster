import { render, screen, fireEvent } from '@testing-library/react';
import Input from '../Input';
import React from 'react';

describe('Input Component', () => {
  it('renders with label', () => {
    render(<Input label="Email" />);
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
  });

  it('shows error message', () => {
    render(<Input label="Email" error="Invalid email" />);
    expect(screen.getByText(/invalid email/i)).toBeInTheDocument();
    const input = screen.getByLabelText(/email/i);
    expect(input).toHaveClass('border-red-300');
  });

  it('calls onChange when value changes', () => {
    const handleChange = jest.fn();
    render(<Input label="Email" onChange={handleChange} />);
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } });
    expect(handleChange).toHaveBeenCalled();
  });

  it('toggles password visibility', () => {
    render(<Input label="Password" type="password" showPasswordToggle />);
    const input = screen.getByLabelText(/password/i);
    expect(input).toHaveAttribute('type', 'password');
    const toggleBtn = screen.getByRole('button');
    fireEvent.click(toggleBtn);
    expect(input).toHaveAttribute('type', 'text');
    fireEvent.click(toggleBtn);
    expect(input).toHaveAttribute('type', 'password');
  });

  it('renders icon if provided', () => {
    render(<Input label="With Icon" icon={<span data-testid="icon">icon</span>} />);
    expect(screen.getByTestId('icon')).toBeInTheDocument();
  });
}); 