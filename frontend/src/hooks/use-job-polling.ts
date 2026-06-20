import { useEffect, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { jobsApi } from "@/lib/api";

const terminalStatuses = new Set(["COMPLETED", "FAILED", "DEAD_LETTER"]);

export function useJobPolling<T>(jobId?: string | null) {
  const queryClient = useQueryClient();
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamFailed, setStreamFailed] = useState(false);

  const query = useQuery({
    queryKey: ["job", jobId],
    queryFn: () => jobsApi.get<T>(jobId!),
    enabled: Boolean(jobId),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (streamFailed) {
        return status && terminalStatuses.has(status) ? false : 2000;
      }
      return false;
    },
  });

  useEffect(() => {
    if (!jobId) {
      setIsStreaming(false);
      setStreamFailed(false);
      return;
    }

    const status = query.data?.status;
    if (status && terminalStatuses.has(status)) {
      return;
    }

    const controller = new AbortController();
    setIsStreaming(true);
    setStreamFailed(false);

    void jobsApi
      .stream<T>(jobId, {
        signal: controller.signal,
        onMessage: (job) => {
          queryClient.setQueryData(["job", jobId], job);
        },
      })
      .catch((error: unknown) => {
        if (controller.signal.aborted) {
          return;
        }
        setStreamFailed(true);
        console.error(error);
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setIsStreaming(false);
        }
      });

    return () => {
      controller.abort();
      setIsStreaming(false);
    };
  }, [jobId, query.data?.status, queryClient]);

  return {
    ...query,
    isFetching: query.isFetching || isStreaming,
  };
}
