from typing import TypedDict


class Lang(TypedDict):
    RegisterChannelsHeader: str           # Channels
    ChannelCardActive: str                # Active
    ChannelCardInactive: str              # Inactive
    ChannelCardRead: str                  # R
    ChannelCardWrite: str                 # W
    ChannelCardAdd: str                   # Add Channel
    SomethingWentWrongError: str          # Something went wrong
    ChannelSettingsMenuMainSettings: str  # Main settings
    ChannelSettingsMenuKeys: str          # Keys
    ChannelSettingsMenuMixins: str        # Mixins
    MixinsIn: str                         # In
    MixinsOut: str                        # Out
    WrongKeyError: str                    # Wrong key
    ReadKeyForm: str                      # Read key
    CreateMixinButton: str                # Create
    YourMixinsHeader: str                 # Your mixins
    ChannelNameForm: str                  # Channel name
    ChannelNameTooLong: str               # Channel name too long
    RenameChannelButton: str              # Rename
    KeyNameTooLongError: str              # Key name too long
    KeyNameForm: str                      # Name
    KeyTypeReadForm: str                  # Read
    KeyTypeWriteForm: str                 # Write
    KeyAllowInfoForm: str                 # Allow info
    CreateKeyButton: str                  # Create
    PauseKeyButton: str                   # Pause
    ResumeKeyButton: str                  # Resume
    DeleteKeyButton: str                  # Delete
    DeleteMixinConfirmQuestion: str       # Delete mixin?
    DeleteMixinButton: str                # Delete
    NoMixinInCard: str                    # You haven't in mixins
    NoMixinOutCard: str                   # You haven't out mixins
    CreateChannelButton: str              # Create
    LoginButton: str                      # Login
    ExitButton: str                       # Exit
    SettingsButton: str                   # Settings
    PasswordTooShortError: str            # Password too short
    InvalidEmailError: str                # Invalid email address
    EmailForm: str                        # Email
    PasswordForm: str                     # Password
    RememberMeForm: str                   # Remember me
    PasswordsNotMatchError: str           # Passwords don't match
    UsernameTooLongError: str             # Username too long
    UsernameForm: str                     # Username
    PasswordAgainForm: str                # Password again
    RegisterButton: str                   # Register
    UserSettingsMenuUsername: str         # Change username
    UserSettingsMenuEmail: str            # Change email
    UserSettingsMenuPassword: str         # Change password
    ChangeEmailButton: str                # Change email
    RenameUserButton: str                 # Rename
    OldPasswordForm: str                  # Old password
    NewPasswordForm: str                  # New password
    NewPasswordAgainForm: str             # New password again
    ChangePasswordButton: str             # Change password
