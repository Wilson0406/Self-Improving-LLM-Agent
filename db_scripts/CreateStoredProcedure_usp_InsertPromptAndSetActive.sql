CREATE PROCEDURE usp_InsertPromptAndSetActive
    @PromptTitle NVARCHAR(200),
    @PromptText NVARCHAR(MAX),
    @UseCase NVARCHAR(100),
    @EffectivenessScore DECIMAL(5,2) = NULL,
    @Feedback NVARCHAR(MAX)
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRANSACTION;

    -- 1. Set all existing prompts for this use case to inactive
    UPDATE model_prompt_library
    SET IsActive = 0
    WHERE UseCase = @UseCase;

    -- 2. Insert the new prompt as active
    INSERT INTO model_prompt_library
      (PromptTitle, PromptText, UseCase, EffectivenessScore, IsActive, LastModifiedTime, FeedbackRequested)
    VALUES
      (@PromptTitle, @PromptText, @UseCase, @EffectivenessScore, 1, GETDATE(), @Feedback);
    COMMIT TRANSACTION;
END
GO