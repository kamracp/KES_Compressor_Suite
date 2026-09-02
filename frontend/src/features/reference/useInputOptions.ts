import { useQuery } from "@tanstack/react-query";

import { fetchInputOptions } from "./referenceService";
import type { InputOptionsResponse } from "./referenceTypes";

// Reference options change only with a backend deploy, so cache them for the
// session: one request serves every page that renders these dropdowns.
export function useInputOptions(accessToken: string | null) {
  return useQuery<InputOptionsResponse>({
    queryKey: ["reference", "input-options"],
    queryFn: () => fetchInputOptions(accessToken as string),
    enabled: accessToken !== null,
    staleTime: Infinity,
  });
}
