import {
  http,
  HttpResponse,
} from "msw";
import {
  describe,
  expect,
  it,
  vi,
} from "vitest";

import { API_BASE_URL } from "../lib/apiConfig";
import {
  ApiError,
  apiRequest,
  AUTH_UNAUTHORIZED_EVENT,
} from "./apiClient";
import { server } from "../test/mocks/server";

describe("apiRequest", () => {
  it("sends authenticated JSON requests and returns parsed data", async () => {
    let authorizationHeader: string | null = null;
    let acceptHeader: string | null = null;

    server.use(
      http.get(
        `${API_BASE_URL}/projects/42`,
        ({ request }) => {
          authorizationHeader =
            request.headers.get("Authorization");
          acceptHeader =
            request.headers.get("Accept");

          return HttpResponse.json({
            id: 42,
            project_code: "S15-M4-TEST",
          });
        },
      ),
    );

    await expect(
      apiRequest<{
        id: number;
        project_code: string;
      }>(
        "/projects/42",
        {
          accessToken: "test-access-token",
        },
      ),
    ).resolves.toEqual({
      id: 42,
      project_code: "S15-M4-TEST",
    });

    expect(authorizationHeader).toBe(
      "Bearer test-access-token",
    );
    expect(acceptHeader).toBe(
      "application/json",
    );
  });

  it("returns undefined for successful no-content responses", async () => {
    server.use(
      http.delete(
        `${API_BASE_URL}/projects/42`,
        () => new HttpResponse(
          null,
          {
            status: 204,
          },
        ),
      ),
    );

    await expect(
      apiRequest<void>(
        "/projects/42",
        {
          method: "DELETE",
          accessToken: "test-access-token",
        },
      ),
    ).resolves.toBeUndefined();
  });

  it("preserves API status and structured error details", async () => {
    server.use(
      http.get(
        `${API_BASE_URL}/projects/42`,
        () => HttpResponse.json(
          {
            detail: "Project access denied.",
          },
          {
            status: 403,
          },
        ),
      ),
    );

    await expect(
      apiRequest(
        "/projects/42",
        {
          accessToken: "test-access-token",
        },
      ),
    ).rejects.toMatchObject({
      name: "ApiError",
      status: 403,
      details: {
        detail: "Project access denied.",
      },
    });
  });

  it("dispatches the unauthorized event for authenticated 401 responses", async () => {
    const unauthorizedListener = vi.fn(
      (_event: Event) => undefined,
    );

    window.addEventListener(
      AUTH_UNAUTHORIZED_EVENT,
      unauthorizedListener,
    );

    server.use(
      http.get(
        `${API_BASE_URL}/projects/42`,
        () => HttpResponse.json(
          {
            detail: "Session expired.",
          },
          {
            status: 401,
          },
        ),
      ),
    );

    try {
      await expect(
        apiRequest(
          "/projects/42",
          {
            accessToken: "expired-token",
          },
        ),
      ).rejects.toBeInstanceOf(ApiError);

      expect(
        unauthorizedListener,
      ).toHaveBeenCalledTimes(1);
    } finally {
      window.removeEventListener(
        AUTH_UNAUTHORIZED_EVENT,
        unauthorizedListener,
      );
    }
  });
});