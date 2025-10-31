import MockAdapter from "axios-mock-adapter";
import axiosClient, { setAuthToken } from "../api/axiosClient.js";

describe("axiosClient", () => {
  it("attaches bearer token when set", async () => {
    const mock = new MockAdapter(axiosClient);
    setAuthToken("test-token");

    mock.onGet("/secure").reply((config) => {
      return [200, { authHeader: config.headers.Authorization }];
    });

    const { data } = await axiosClient.get("/secure");
    expect(data.authHeader).toBe("Bearer test-token");

    mock.restore();
  });

  it("omits authorization header when token cleared", async () => {
    const mock = new MockAdapter(axiosClient);
    setAuthToken(null);

    mock.onGet("/secure").reply((config) => {
      return [200, { hasAuthorization: Boolean(config.headers.Authorization) }];
    });

    const { data } = await axiosClient.get("/secure");
    expect(data.hasAuthorization).toBe(false);

    mock.restore();
  });
});
