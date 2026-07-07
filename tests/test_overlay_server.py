import base64

from widgetable_solver.overlay_server import (
    INDEX_HTML,
    OverlayServerError,
    OverlayThreadingHTTPServer,
    parse_image_data_url,
)


def test_parse_image_data_url_accepts_png_payload():
    encoded = base64.b64encode(b"png-bytes").decode("ascii")

    result = parse_image_data_url(f"data:image/png;base64,{encoded}")

    assert result == b"png-bytes"


def test_parse_image_data_url_rejects_non_images():
    encoded = base64.b64encode(b"text").decode("ascii")

    try:
        parse_image_data_url(f"data:text/plain;base64,{encoded}")
    except OverlayServerError as error:
        assert str(error) == "Expected an image data URL"
    else:
        raise AssertionError("Expected OverlayServerError")


def test_index_html_supports_paste_drop_and_file_upload():
    assert "paste" in INDEX_HTML
    assert "drop" in INDEX_HTML
    assert 'type="file"' in INDEX_HTML
    assert "/analyze" in INDEX_HTML


def test_index_html_does_not_expose_internal_grid_controls():
    assert "gridWidth" not in INDEX_HTML
    assert "gridHeight" not in INDEX_HTML
    assert "Grid width" not in INDEX_HTML
    assert "Grid height" not in INDEX_HTML


def test_index_html_defaults_to_fast_strategy_for_live_overlays():
    assert '<option value="fast" selected>fast</option>' in INDEX_HTML


def test_overlay_server_uses_daemon_request_threads():
    assert OverlayThreadingHTTPServer.daemon_threads is True
