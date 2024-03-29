#   _        _   _     _       _                       __  __  ____
#  | |      (_) | |   | |     (_)                     |  \/  |/ __ \
#  | |       _  | |_  | |__    _   _   _   _ __ ___   | \  / | |  | |
#  | |      | | | __| | "_ \  | | | | | | | "_ ` _ \  | |\/| | |  | |
#  | |____  | | | |_  | | | | | | | |_| | | | | | | | | |  | | |__| |
#  |______| |_|  \__| |_| |_| |_|  \__,_| |_| |_| |_| |_|  |_|\___\_\

class Error:
    code: int
    description: str


class Ok(Error):
    code = 200
    description = 'Ok'


class ChannelError(Error):
    ...


class GrantError(Error):
    ...


class MixinError(Error):
    ...


class ServiceError(Error):
    ...


class UserError(Error):
    ...


class ChannelNameError(ChannelError):
    code = 700
    description = "Bad channel name"


class ChannelNotExistError(ChannelError):
    code = 701
    description = "Channel doesn't exist"


class NotChannelOwnerError(ChannelError):
    code = 702
    description = "No access to this channel"


class ChannelMaxMessageSizeLimitOver(ChannelError):
    code = 703
    description = "Max message size limit over"


class ChannelBufferLimitOver(ChannelError):
    code = 704
    description = "Buffer limit over"


class ChannelBufferedMessageCountLimitOver(ChannelError):
    code = 705
    description = "Buffered message count limit over"


class ChannelBufferedDataTTLOver(ChannelError):
    code = 706
    description = "Buffered data TTL over"


class ChannelEndToEndNotAvailable(ChannelError):
    code = 707
    description = "End-to-end data encryption not available " \
                  "on your account plan"


class KeyNameError(GrantError):
    code = 800
    description = "Bad key name"


class KeyPermissionsError(GrantError):
    code = 801
    description = "Wrong permissions"


class BadChannelIdError(GrantError):
    code = 802
    description = "Bad channel id"


class BadKeyError(GrantError):
    code = 803
    description = "Invalid key"


class AlreadyMixedError(MixinError):
    code = 900
    description = "Already mixed"


class BadThreadError(MixinError):
    code = 901
    description = "Bad thread"


class BadKeyTypeError(MixinError):
    code = 902
    description = "Bad thread type"


class CircleMixinError(MixinError):
    code = 903
    description = "You want to make a circle"


class SelfMixinError(MixinError):
    code = 904
    description = "Mixin with same channel"


class EmailError(UserError):
    code = 1000
    description = "Bad Email"


class UsernameError(UserError):
    code = 1001
    description = "Bad username"


class PasswordError(UserError):
    code = 1002
    description = "Bad password"


class EmailExistError(UserError):
    code = 1003
    description = "User with this email already exists"


class BadUserError(UserError):
    code = 1004
    description = "User not found"


class TooManyRequestsError(ServiceError):
    code = 1100
    description = 'Too many requests'


class ChannelLimitOver(ServiceError):
    code = 1101
    description = "You can't create channel because of limit"
