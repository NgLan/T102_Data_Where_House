"use client";

import { useCallback, useEffect, useState } from "react";
import type { DataSourceResponse, UpdateDataSourceColumnRequest } from "@/api";
import { isApiError } from "@/common/errors/api-error";
import { useAppNotification } from "@/common/hooks/use-app-notification";
import {
  deleteDataSource,
  listDataSources,
  updateDataSourceColumn,
  uploadDataSources,
} from "../services/data-source-service";

const MAX_FILES = 20;
const MAX_FILE_SIZE = 20 * 1024 * 1024;
const ALLOWED_EXTENSIONS = [".csv", ".docx"];

/** Quản lý lifecycle Data Source thật, không tạo preview/sample phía client.
 * @param projectId ID Project sở hữu các Data Source.
 * @param onRequirementExtracted Callback nhận requirement trích xuất từ DOCX.
 * @returns State nguồn dữ liệu cùng các thao tác upload, cập nhật và xóa.
 */
export function useDataSources(
  projectId: string,
  onRequirementExtracted: (value: string) => void,
) {
  const { notifyError, notifySuccess } = useAppNotification();
  const [sources, setSources] = useState<DataSourceResponse[]>([]);
  const [canEdit, setCanEdit] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isMutating, setIsMutating] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);

  const reload = useCallback(async () => {
    setIsLoading(true);
    setLoadError(null);
    try {
      const result = await listDataSources(projectId);
      setSources(result.items ?? []);
      setCanEdit(result.can_edit);
    } catch (error) {
      setLoadError(errorCodeOf(error));
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    let active = true;
    void listDataSources(projectId)
      .then((result) => {
        if (!active) return;
        setSources(result.items ?? []);
        setCanEdit(result.can_edit);
      })
      .catch((error) => { if (active) setLoadError(errorCodeOf(error)); })
      .finally(() => { if (active) setIsLoading(false); });
    return () => { active = false; };
  }, [projectId]);

  const uploadFiles = useCallback(async (files: File[]) => {
    const validationError = validateFiles(files);
    if (validationError) return notifyError(validationError);
    setIsMutating(true);
    try {
      const result = await uploadDataSources(projectId, files);
      if (result.extracted_requirement_text) {
        onRequirementExtracted(result.extracted_requirement_text);
      }
      await reload();
      notifySuccess("MSG_ACTION_COMPLETED");
    } catch (error) {
      notifyError(errorCodeOf(error));
    } finally {
      setIsMutating(false);
    }
  }, [notifyError, notifySuccess, onRequirementExtracted, projectId, reload]);

  const updateColumn = useCallback(async (
    sourceId: string,
    body: UpdateDataSourceColumnRequest,
  ) => {
    setIsMutating(true);
    try {
      const updated = await updateDataSourceColumn(projectId, sourceId, body);
      setSources((current) => current.map((item) => item.id === updated.id ? updated : item));
      notifySuccess("MSG_ACTION_COMPLETED");
    } catch (error) {
      notifyError(errorCodeOf(error));
    } finally {
      setIsMutating(false);
    }
  }, [notifyError, notifySuccess, projectId]);

  const deleteSource = useCallback(async (sourceId: string) => {
    setIsMutating(true);
    try {
      await deleteDataSource(projectId, sourceId);
      setSources((current) => current.filter((item) => item.id !== sourceId));
      notifySuccess("MSG_ACTION_COMPLETED");
    } catch (error) {
      notifyError(errorCodeOf(error));
    } finally {
      setIsMutating(false);
    }
  }, [notifyError, notifySuccess, projectId]);

  return {
    canEdit, deleteSource, isLoading, isMutating, loadError,
    reload, sources, updateColumn, uploadFiles,
  };
}

function validateFiles(files: File[]): string | null {
  if (!files.length) return "FILE_EMPTY";
  if (files.length > MAX_FILES) return "MAX_FILES_EXCEEDED";
  if (files.some((file) => file.size > MAX_FILE_SIZE)) return "FILE_TOO_LARGE";
  const invalid = files.some((file) =>
    !ALLOWED_EXTENSIONS.some((extension) => file.name.toLowerCase().endsWith(extension)));
  return invalid ? "INVALID_FILE_FORMAT" : null;
}

function errorCodeOf(error: unknown): string {
  return isApiError(error) ? error.errorCode : "UNKNOWN_ERROR";
}
