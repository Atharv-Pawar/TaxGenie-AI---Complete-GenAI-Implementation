import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";

// Simple smoke tests for key components

// ── MessageBubble ─────────────────────────────────────────────────────────────
jest.mock("framer-motion", () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}));

import MessageBubble from "../../frontend/components/chat/MessageBubble";

describe("MessageBubble", () => {
  it("renders user message correctly", () => {
    render(<MessageBubble role="user" content="What is 80C?" />);
    expect(screen.getByText("What is 80C?")).toBeInTheDocument();
  });

  it("renders assistant message with sources", () => {
    render(
      <MessageBubble
        role="assistant"
        content="Section 80C allows deductions up to ₹1.5L"
        sources={["Section 80C - Deductions"]}
      />
    );
    expect(screen.getByText(/Section 80C allows/)).toBeInTheDocument();
    expect(screen.getByText(/Section 80C - Deductions/)).toBeInTheDocument();
  });

  it("renders follow-up suggestions", () => {
    const onFollowUp = jest.fn();
    render(
      <MessageBubble
        role="assistant"
        content="Here is my answer."
        followUps={["Tell me more", "What about HRA?"]}
        onFollowUp={onFollowUp}
      />
    );
    expect(screen.getByText(/Tell me more/)).toBeInTheDocument();
    expect(screen.getByText(/What about HRA/)).toBeInTheDocument();
  });
});
