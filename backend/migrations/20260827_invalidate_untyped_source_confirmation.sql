UPDATE projects AS project
SET covered_analytical_requirement_revision =
    CASE
        WHEN project.derived_analytical_requirement_revision = 0 THEN 1
        ELSE 0
    END
WHERE EXISTS (
    SELECT 1
    FROM analytical_requirements AS analytical,
         jsonb_array_elements(analytical.source_coverage) AS assessment
    WHERE analytical.project_id = project.id
      AND assessment->>'status' = 'NEEDS_SOURCE_CONFIRMATION'
      AND NOT (assessment ? 'question_type')
);
