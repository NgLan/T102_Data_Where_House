"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { isApiError } from "@/api";
import { sandboxDeploymentQueryKeys } from "../../../constants/sandbox-deployment-query-keys";
import type { DdlDialect } from "../../../constants/supported-ddl-dialects";
import { generateDataModelDdl } from "../services/data-model-ddl-api";
import { useDdlEditorActions } from "./use-ddl-editor-actions";

/** Quản lý generated DDL query và draft đang chỉnh sửa trong editor. */
export function useDdlEditor(projectId: string, databaseName: string) {
  const [dialect, setDialect] = useState<DdlDialect>("POSTGRESQL");
  const [draft, setDraft] = useState<{
    dialect: DdlDialect;
    sourceDdl: string;
    value: string;
  } | null>(null);
  const query = useQuery({
    queryKey: sandboxDeploymentQueryKeys.ddl(projectId, dialect),
    queryFn: () => generateDataModelDdl(projectId, dialect),
    refetchOnWindowFocus: false,
  });
  const sourceDdl = query.data?.ddl ?? "";
  const ddlCode = draft?.dialect === dialect && draft.sourceDdl === sourceDdl
    ? draft.value
    : sourceDdl;
  const setDdlCode = (value: string) => setDraft({ dialect, sourceDdl, value });
  const actions = useDdlEditorActions({
    ddlCode,
    dialect,
    databaseName,
    onDdlCodeChange: setDdlCode,
  });
  const handleDialectChange = (value: DdlDialect) => {
    setDraft(null);
    setDialect(value);
  };
  return {
    ...actions,
    ddlCode,
    dialect,
    errorCode: isApiError(query.error) ? query.error.errorCode : "UNKNOWN_ERROR",
    isInitialError: query.isError && !query.data,
    isInitialLoading: query.isPending,
    isRefreshing: query.isFetching,
    retry: query.refetch,
    setDdlCode,
    setDialect: handleDialectChange,
  };
}
