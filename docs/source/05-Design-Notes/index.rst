.. _design-notes:

Design Notes
==============================================================================
This page explains why ``simple_aws_lambda`` is built the way it is. Read it when you want to extend the library or wonder why an API looks the way it does. For how to use it, start with :ref:`quick-start`.


Three Layers
------------------------------------------------------------------------------
The library has three modules, each built on the one before:

- :mod:`simple_aws_lambda.model`: objects that wrap boto3 responses, see :ref:`data-model`.
- :mod:`simple_aws_lambda.client`: one function per boto3 call. Each one takes a boto3 Lambda client, handles pagination, and returns model objects.
- :mod:`simple_aws_lambda.recipe`: tasks that take several calls, such as :ref:`cleanup-old-layer-versions` and :ref:`cross-account-layer-access`.

Users import all of them from ``simple_aws_lambda.api``. Anything not exported there is internal.


Keep the Raw Response
------------------------------------------------------------------------------
Every model stores the boto3 response unchanged in ``_data``, and exposes its fields as read-only properties:

.. code-block:: python

    @dataclasses.dataclass(frozen=True)
    class LayerVersion(Base):
        _data: LayerVersionsListItemTypeDef | GetLayerVersionResponseTypeDef

        @property
        def version(self) -> int:
            return self._data["Version"]

This is deliberate:

- **No data is lost.** AWS adds response fields over time. A field the library has no property for yet is still in ``_data``.
- **A model never fails to load.** The constructor does not parse or validate anything, so an unexpected response shape cannot break it. Only the property you read touches the data.
- **Properties can add meaning.** Besides plain fields, a model offers derived values that boto3 does not, such as :attr:`LayerVersion.layer_name <simple_aws_lambda.model.LayerVersion.layer_name>` (parsed from the ARN) and :attr:`LayerVersion.created_datetime <simple_aws_lambda.model.LayerVersion.created_datetime>` (a timezone aware datetime).

Required fields are read with ``self._data["Key"]``, optional ones with ``self._data.get("Key")``, following the boto3 response documentation.

Each model also has ``core_data``, a short dictionary of its essential fields, for logging and debugging without printing the whole response.


Iterators Instead of Lists
------------------------------------------------------------------------------
List functions such as :func:`~simple_aws_lambda.client.list_layer_versions` return an :class:`~simple_aws_lambda.model.LayerVersionIterproxy` built on `iterproxy <https://github.com/MacHu-GWU/iterproxy-project>`_. Pages are fetched only as you iterate, so stopping early stops the API calls. Call ``.all()`` for a list, or ``.one()``, ``.many(n)`` and similar methods for part of it.


Not Found Is Not an Error
------------------------------------------------------------------------------
:func:`~simple_aws_lambda.client.get_layer_version` and :func:`~simple_aws_lambda.recipe.get_latest_layer_version` return ``None`` when the version does not exist, instead of raising ``ResourceNotFoundException``. "Does it exist?" is a normal question in deployment code, and ``if layer_version is None`` reads better than a ``try`` block. Any other AWS error is still raised.


Recipes Are Idempotent
------------------------------------------------------------------------------
A recipe can be called again with the same arguments without harm, so it is safe in a deployment script that runs on every release:

- Granting access that already exists, or revoking access that does not, does nothing. This works because the statement id is derived from the principal and the action, so the same grant always uses the same id.
- :func:`~simple_aws_lambda.recipe.cleanup_old_layer_versions` only deletes versions outside the retention rules. A second run finds nothing to delete. It also defaults to ``real_run=False``, so a mistake in the arguments only prints a preview.


Testing Without AWS
------------------------------------------------------------------------------
The unit tests and the notebook pages of these docs run against `moto <https://docs.getmoto.org/>`_, which fakes AWS in memory. No AWS account or credentials are needed.

Some functions have a private ``_sort_descending`` argument. Older moto versions returned layer versions oldest first, while AWS returns the newest first; the argument sorts the result in memory to match AWS. Against real AWS you never need it.
