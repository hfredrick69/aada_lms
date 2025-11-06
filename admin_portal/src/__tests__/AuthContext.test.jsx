import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AuthProvider, useAuth } from "../context/AuthContext.jsx";

vi.mock("../api/auth.js", () => ({
  login: vi.fn(async () => ({
    access_token: "abc123"
  })),
  me: vi.fn(async () => ({
    id: "user-1",
    email: "admin@aada.edu",
    first_name: "Admin",
    last_name: "User",
    roles: ["admin", "finance"]
  }))
}));

const TestComponent = () => {
  const { login, user, token, logout } = useAuth();

  const handleLogin = async () => {
    await login({ email: "admin@aada.edu", password: "secret" });
  };

  return (
    <div>
      <button onClick={handleLogin}>Sign in</button>
      <button onClick={logout}>Sign out</button>
      <span data-testid="token">{token || ""}</span>
      <span data-testid="user-email">{user?.email || ""}</span>
    </div>
  );
};

describe("AuthContext", () => {
  it("logs in and stores normalized user data", async () => {
    const user = userEvent.setup();
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await user.click(screen.getByText("Sign in"));

    await waitFor(() => {
      expect(screen.getByTestId("token")).toHaveTextContent("abc123");
      expect(screen.getByTestId("user-email")).toHaveTextContent("admin@aada.edu");
    });
  });

  it("clears auth state on logout", async () => {
    const user = userEvent.setup();
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await user.click(screen.getByText("Sign in"));
    await waitFor(() => expect(screen.getByTestId("token")).toHaveTextContent("abc123"));

    await user.click(screen.getByText("Sign out"));
    await waitFor(() => {
      expect(screen.getByTestId("token")).toHaveTextContent("");
      expect(screen.getByTestId("user-email")).toHaveTextContent("");
    });
  });
});
