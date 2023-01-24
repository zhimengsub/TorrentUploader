from typing import Any, Optional, TYPE_CHECKING, Union

from httpcore import URL
from httpx import Client, Cookies, Response

# noinspection PyProtectedMember
from httpx._client import USE_CLIENT_DEFAULT, UseClientDefault
from pydantic import PrivateAttr

from models import BaseModel

if TYPE_CHECKING:
    # noinspection PyProtectedMember
    from httpx._types import (
        AuthTypes,
        CookieTypes,
        HeaderTypes,
        QueryParamTypes,
        RequestContent,
        RequestData,
        RequestExtensions,
        RequestFiles,
        TimeoutTypes,
        URLTypes,
    )


class Net(BaseModel):
    _client: Optional[Client] = PrivateAttr(None)

    base_url: URL
    cookies: Optional[Cookies] = None

    class Config(BaseModel.Config):
        arbitrary_types_allowed = True

    @property
    def client(self) -> Client:
        if self._client is None:
            self._client = Client(
                base_url=self.base_url,
                headers={
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0",
                    "cache-control": "no-cache",
                    "DNT": "1",
                    "host": str(self.base_url.host),
                    "origin": str(self.base_url.origin),
                    "referer": str(self.base_url.origin) + "/",
                },
                cookies=self.cookies,
            )
        return self._client

    def get(
        self,
        url: "URLTypes",
        *,
        params: Optional["QueryParamTypes"] = None,
        headers: Optional["HeaderTypes"] = None,
        cookies: Optional["CookieTypes"] = None,
        auth: Union["AuthTypes", "UseClientDefault"] = USE_CLIENT_DEFAULT,
        follow_redirects: Union[bool, "UseClientDefault"] = USE_CLIENT_DEFAULT,
        timeout: Union["TimeoutTypes", "UseClientDefault"] = USE_CLIENT_DEFAULT,
        extensions: Optional["RequestExtensions"] = None,
    ) -> Response:
        return self.client.get(
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )

    def post(
        self,
        url: "URLTypes",
        *,
        content: Optional["RequestContent"] = None,
        data: Optional["RequestData"] = None,
        files: Optional["RequestFiles"] = None,
        json: Optional[Any] = None,
        params: Optional["QueryParamTypes"] = None,
        headers: Optional["HeaderTypes"] = None,
        cookies: Optional["CookieTypes"] = None,
        auth: Union["AuthTypes", "UseClientDefault"] = USE_CLIENT_DEFAULT,
        follow_redirects: Union[bool, "UseClientDefault"] = USE_CLIENT_DEFAULT,
        timeout: Union[
            "TimeoutTypes", f"UseClientDefault"
        ] = USE_CLIENT_DEFAULT,
        extensions: Optional["RequestExtensions"] = None,
    ) -> "Response":
        return self.client.post(
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )
