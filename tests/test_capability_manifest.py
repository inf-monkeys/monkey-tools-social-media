import unittest

from src.capability_manifest import publish_openapi_tool_capability_manifests


class CapabilityManifestTest(unittest.TestCase):
    def test_publishes_canonical_manifest(self):
        document = {
            "paths": {
                "/run": {
                    "post": {
                        "x-monkey-tool-name": "sample",
                        "x-monkey-tool-input": [
                            {"name": "items", "type": "array", "required": True}
                        ],
                        "x-monkey-tool-output": [{"name": "result", "type": "string"}],
                    }
                }
            }
        }
        manifest = publish_openapi_tool_capability_manifests(
            document, "tools", "owner-repo"
        )["paths"]["/run"]["post"]["x-monkeys-capability-manifest"]
        self.assertEqual(manifest["id"], "tools_sample")
        self.assertEqual(manifest["ownerRepo"], "owner-repo")
        self.assertTrue(manifest["ports"]["inputs"][0]["multiple"])
        self.assertTrue(manifest["ports"]["inputs"][0]["required"])

    def test_rejects_conflicting_port_declarations(self):
        document = {
            "paths": {
                "/run": {
                    "post": {
                        "x-monkey-tool-name": "sample",
                        "x-monkey-tool-input": [
                            {"name": "value", "type": "string"},
                            {"name": "value", "type": "array"},
                        ],
                    }
                }
            }
        }
        with self.assertRaises(ValueError):
            publish_openapi_tool_capability_manifests(
                document, "tools", "owner-repo"
            )


if __name__ == "__main__":
    unittest.main()
