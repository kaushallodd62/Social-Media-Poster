import { render, screen, fireEvent } from '@testing-library/react';
import Alert from '../Alert';
import React from 'react';

describe('Alert Component', () => {
  it('renders info alert by default', () => {
    render(<Alert message="Info message" />);
    expect(screen.getByText(/info message/i)).toBeInTheDocument();
    expect(screen.getByRole('img', { hidden: true })).toBeInTheDocument();
  });

  it('renders success, error, and warning alerts', () => {
    render(<Alert type="success" message="Success!" />);
    expect(screen.getByText(/success!/i)).toBeInTheDocument();
    render(<Alert type="error" message="Error!" />);
    expect(screen.getByText(/error!/i)).toBeInTheDocument();
    render(<Alert type="warning" message="Warning!" />);
    expect(screen.getByText(/warning!/i)).toBeInTheDocument();
  });

  it('renders title if provided', () => {
    render(<Alert title="Alert Title" message="Alert message" />);
    expect(screen.getByText(/alert title/i)).toBeInTheDocument();
    expect(screen.getByText(/alert message/i)).toBeInTheDocument();
  });

  it('renders dismiss button if dismissible', () => {
    const onDismiss = jest.fn();
    render(<Alert message="Dismiss me" dismissible onDismiss={onDismiss} />);
    const btn = screen.getByRole('button', { name: /dismiss/i });
    expect(btn).toBeInTheDocument();
    fireEvent.click(btn);
    expect(onDismiss).toHaveBeenCalled();
  });
}); 