CREATE PROCEDURE usp_FetchAndLockNextDocument
    @CurrentStatus NVARCHAR(50) = 'Submitted',
    @NextStatus NVARCHAR(50) = 'Processing',
    @AssignedTo NVARCHAR(100) = NULL
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @DocumentID INT;

    BEGIN TRANSACTION;

    -- Fetch and lock the next available document
    SELECT TOP 1
        @DocumentID = DocumentID
    FROM
        document_master WITH (ROWLOCK, UPDLOCK, READPAST)
    WHERE
        ExtractionStatus = @CurrentStatus
    ORDER BY
        CreatedTime; -- You may change the order based on priority

    IF @DocumentID IS NOT NULL
    BEGIN
        -- Mark the document as 'Processing' (locked)
        UPDATE document_master
        SET 
            ExtractionStatus = @NextStatus,
            LastUpdated = GETDATE(),
			PickedTime = GETDATE(),
            UserID = @AssignedTo
        WHERE
            DocumentID = @DocumentID;

        -- Return the locked document
        SELECT *
        FROM document_master
        WHERE DocumentID = @DocumentID;

        COMMIT TRANSACTION;
    END
    ELSE
    BEGIN
        -- Nothing available
        ROLLBACK TRANSACTION;
        SELECT NULL AS DocumentID;
    END
END
GO