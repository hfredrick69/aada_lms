import { render, screen } from "@testing-library/react";
import RoleGate from "../components/RoleGate.jsx";
import { AuthProvider } from "../context/AuthContext.jsx";

vi.mock("../context/AuthContext.jsx", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useAuth: () => ({
      hasRole: (roles) => roles.includes("Admin")
    })
  };
});

describe("RoleGate", () => {
  it("renders children when role permitted", () => {
    render(
      <RoleGate allowedRoles={["Admin"]}>
        <span>Allowed content</span>
      </RoleGate>
    );
    expect(screen.getByText("Allowed content")).toBeInTheDocument();
  });

  it("renders placeholder when role not permitted", () => {
    render(
      <RoleGate allowedRoles={["Finance"]}>
        <span>Secret</span>
      </RoleGate>
    );
    expect(screen.queryByText("Secret")).not.toBeInTheDocument();
    expect(screen.getByText(/restricted/i)).toBeInTheDocument();
  });
});
