from daiana.config.settings import load_settings, mask_secret as _mask_secret


def check_api() -> dict:
    s = load_settings()
    return {
        "provider": s.provider,
        "base_url": s.base_url,
        "model": s.model,
        "api_key_name": s.api_key_name,
        "api_key_masked": _mask_secret(s.api_key_value),
    }
