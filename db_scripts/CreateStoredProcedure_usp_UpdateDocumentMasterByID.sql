CREATE PROCEDURE usp_UpdateDocumentMasterByID
    @DocumentID INT,
    @ExtractionStatus NVARCHAR(50),
	@ExtractionOutput NVARCHAR(MAX),
    @PromptID INT,
    @RetryCount INT,
	@ErrorMessage NVARCHAR(MAX),
	@Comments NVARCHAR(MAX)
AS
BEGIN
    SET NOCOUNT ON;

    UPDATE document_master
    SET 
        ExtractionStatus = ISNULL(@ExtractionStatus, ExtractionStatus),
		ExtractionOutput = ISNULL(@ExtractionOutput, ExtractionOutput),
        PromptID = ISNULL(@PromptID, PromptID),
        ErrorMessage = ISNULL(@ErrorMessage, ErrorMessage),
        Comments = ISNULL(@Comments, Comments),
		RetryCount = ISNULL(@RetryCount, RetryCount),
        LastUpdated = GETDATE(),
		CompletedTime = GETDATE()
    WHERE
        DocumentID = @DocumentID;

END
GO