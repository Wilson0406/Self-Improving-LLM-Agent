CREATE PROCEDURE usp_InsertDocumentRequest
    @FileName NVARCHAR(255),
    @UserID NVARCHAR(100) = NULL,
    @SourceType NVARCHAR(50) = NULL
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO document_master (
        FileName,
        ExtractionStatus,
        CreatedTime,
        LastUpdated,
        UserID,
        SourceType,
        RetryCount
    )
    VALUES (
        @FileName,
        'Submitted',
        GETDATE(),
        GETDATE(),
        @UserID,
        @SourceType,
        0                  -- RetryCount is 0 for fresh requests
    );
END;
GO