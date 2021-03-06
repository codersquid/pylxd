# Copyright (c) 2016 Canonical Ltd
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import hashlib

from pylxd import exceptions, model
from pylxd.operation import Operation


class Image(model.Model):
    """A LXD Image."""
    aliases = model.Attribute()
    auto_update = model.Attribute()
    architecture = model.Attribute()
    cached = model.Attribute()
    created_at = model.Attribute()
    expires_at = model.Attribute()
    filename = model.Attribute()
    fingerprint = model.Attribute()
    last_used_at = model.Attribute()
    properties = model.Attribute()
    public = model.Attribute()
    size = model.Attribute()
    uploaded_at = model.Attribute()

    @property
    def api(self):
        return self.client.api.images[self.fingerprint]

    @classmethod
    def get(cls, client, fingerprint):
        """Get an image."""
        try:
            response = client.api.images[fingerprint].get()
        except exceptions.LXDAPIException as e:
            if e.response.status_code == 404:
                raise exceptions.NotFound()
            raise

        image = cls(client, **response.json()['metadata'])
        return image

    @classmethod
    def all(cls, client):
        """Get all images."""
        response = client.api.images.get()

        images = []
        for url in response.json()['metadata']:
            fingerprint = url.split('/')[-1]
            images.append(cls(client, fingerprint=fingerprint))
        return images

    @classmethod
    def create(cls, client, image_data, public=False, wait=False):
        """Create an image."""
        fingerprint = hashlib.sha256(image_data).hexdigest()

        headers = {}
        if public:
            headers['X-LXD-Public'] = '1'
        try:
            response = client.api.images.post(
                data=image_data, headers=headers)
        except exceptions.LXDAPIException as e:
            raise exceptions.CreateFailed(e.response.json())

        if wait:
            Operation.wait_for_operation(client, response.json()['operation'])
        return cls(client, fingerprint=fingerprint)

    def export(self):
        """Export the image."""
        try:
            response = self.api.export.get()
        except exceptions.LXDAPIException as e:
            if e.response.status_code == 404:
                raise exceptions.NotFound()
            raise

        return response.content
