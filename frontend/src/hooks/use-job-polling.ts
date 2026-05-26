import { useQuery } from "@tanstack/react-query";
import { jobsApi } from "@/lib/api";

const terminalStatuses = new Set(["COMPLETED", "FAILED", "DEAD_LETTER"]);

export function useJobPolling<T>(jobId?: string | null) {
  return useQuery({
    queryKey: ["job", jobId],
    queryFn: () => jobsApi.get<T>(jobId!),
    enabled: Boolean(jobId),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status && terminalStatuses.has(status) ? false : 2000;
    },
  });
}
