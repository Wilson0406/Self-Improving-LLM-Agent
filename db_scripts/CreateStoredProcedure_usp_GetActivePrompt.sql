CREATE PROCEDURE usp_GetActivePrompt
    @UseCase NVARCHAR(100) = NULL
AS
BEGIN
	SET NOCOUNT ON;
    
    SELECT TOP 1
		PromptID,
        PromptTitle,
        PromptText,
        UseCase,
        EffectivenessScore
	FROM
		model_prompt_library
	WHERE
		IsActive = 1
        AND (@UseCase IS NULL OR UseCase = @UseCase)
	ORDER BY
		EffectivenessScore DESC,
        LastModifiedTime DESC;
END;
GO