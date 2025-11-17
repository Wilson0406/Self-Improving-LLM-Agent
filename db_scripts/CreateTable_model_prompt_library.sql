CREATE TABLE model_prompt_library (
    PromptID INT IDENTITY(1,1) PRIMARY KEY,
    PromptTitle NVARCHAR(200) NOT NULL,
    PromptText NVARCHAR(MAX) NOT NULL,
    UseCase NVARCHAR(100) NULL,						-- E.g., 'Form926 Extraction', 'Entity Recognition'
    IsActive BIT DEFAULT 0,							-- Switch for prompt deployment
    CreatedBy NVARCHAR(100) NULL,
    CreatedTime DATETIME DEFAULT GETDATE(),
    LastModifiedBy NVARCHAR(100) NULL,
    LastModifiedTime DATETIME DEFAULT GETDATE(),
    EffectivenessScore DECIMAL(3,2) NULL,			-- Optional: feedback/score
    Comments NVARCHAR(500) NULL,
    FeedbackRequested NVARCHAR(MAX) NULL
);