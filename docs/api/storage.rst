Storage
=======

*This CDP domain is experimental.*

.. module:: cdp.storage

* Types_
* Commands_
* Events_

Types
-----

Generally, you do not need to instantiate CDP types
yourself. Instead, the API creates objects for you as return
values from commands, and then you can use those objects as
arguments to other commands.

.. autoclass:: SerializedStorageKey
      :members:
      :undoc-members:
      :exclude-members: from_json, to_json

.. autoclass:: StorageType
      :members:
      :undoc-members:
      :exclude-members: from_json, to_json

.. autoclass:: UsageForType
      :members:
      :undoc-members:
      :exclude-members: from_json, to_json

.. autoclass:: TrustTokens
      :members:
      :undoc-members:
      :exclude-members: from_json, to_json

.. autoclass:: InterestGroupAccessType
      :members:
      :undoc-members:
      :exclude-members: from_json, to_json

.. autoclass:: InterestGroupAd
      :members:
      :undoc-members:
      :exclude-members: from_json, to_json

.. autoclass:: InterestGroupDetails
      :members:
      :undoc-members:
      :exclude-members: from_json, to_json

.. autoclass:: SharedStorageAccessType
      :members:
      :undoc-members:
      :exclude-members: from_json, to_json

.. autoclass:: SharedStorageEntry
      :members:
      :undoc-members:
      :exclude-members: from_json, to_json

.. autoclass:: SharedStorageMetadata
      :members:
      :undoc-members:
      :exclude-members: from_json, to_json

.. autoclass:: SharedStorageReportingMetadata
      :members:
      :undoc-members:
      :exclude-members: from_json, to_json

.. autoclass:: SharedStorageUrlWithMetadata
      :members:
      :undoc-members:
      :exclude-members: from_json, to_json

.. autoclass:: SharedStorageAccessParams
      :members:
      :undoc-members:
      :exclude-members: from_json, to_json

.. autoclass:: StorageBucketsDurability
      :members:
      :undoc-members:
      :exclude-members: from_json, to_json

.. autoclass:: StorageBucket
      :members:
      :undoc-members:
      :exclude-members: from_json, to_json

.. autoclass:: StorageBucketInfo
      :members:
      :undoc-members:
      :exclude-members: from_json, to_json

.. autoclass:: AttributionReportingSourceType
      :members:
      :undoc-members:
      :exclude-members: from_json, to_json

.. autoclass:: UnsignedInt64AsBase10
      :members:
      :undoc-members:
      :exclude-members: from_json, to_json

.. autoclass:: UnsignedInt128AsBase16
      :members:
      :undoc-members:
      :exclude-members: from_json, to_json

.. autoclass:: SignedInt64AsBase10
      :members:
      :undoc-members:
      :exclude-members: from_json, to_json

.. autoclass:: AttributionReportingFilterDataEntry
      :members:
      :undoc-members:
      :exclude-members: from_json, to_json

.. autoclass:: AttributionReportingAggregationKeysEntry
      :members:
      :undoc-members:
      :exclude-members: from_json, to_json

.. autoclass:: AttributionReportingSourceRegistration
      :members:
      :undoc-members:
      :exclude-members: from_json, to_json

.. autoclass:: AttributionReportingSourceRegistrationResult
      :members:
      :undoc-members:
      :exclude-members: from_json, to_json

Commands
--------

Each command is a generator function. The return
type ``Generator[x, y, z]`` indicates that the generator
*yields* arguments of type ``x``, it must be resumed with
an argument of type ``y``, and it returns type ``z``. In
this library, types ``x`` and ``y`` are the same for all
commands, and ``z`` is the return type you should pay attention
to. For more information, see
:ref:`Getting Started: Commands <getting-started-commands>`.

.. autofunction:: clear_cookies

.. autofunction:: clear_data_for_origin

.. autofunction:: clear_data_for_storage_key

.. autofunction:: clear_shared_storage_entries

.. autofunction:: clear_trust_tokens

.. autofunction:: delete_shared_storage_entry

.. autofunction:: delete_storage_bucket

.. autofunction:: get_cookies

.. autofunction:: get_interest_group_details

.. autofunction:: get_shared_storage_entries

.. autofunction:: get_shared_storage_metadata

.. autofunction:: get_storage_key_for_frame

.. autofunction:: get_trust_tokens

.. autofunction:: get_usage_and_quota

.. autofunction:: override_quota_for_origin

.. autofunction:: reset_shared_storage_budget

.. autofunction:: run_bounce_tracking_mitigations

.. autofunction:: set_attribution_reporting_local_testing_mode

.. autofunction:: set_attribution_reporting_tracking

.. autofunction:: set_cookies

.. autofunction:: set_interest_group_tracking

.. autofunction:: set_shared_storage_entry

.. autofunction:: set_shared_storage_tracking

.. autofunction:: set_storage_bucket_tracking

.. autofunction:: track_cache_storage_for_origin

.. autofunction:: track_cache_storage_for_storage_key

.. autofunction:: track_indexed_db_for_origin

.. autofunction:: track_indexed_db_for_storage_key

.. autofunction:: untrack_cache_storage_for_origin

.. autofunction:: untrack_cache_storage_for_storage_key

.. autofunction:: untrack_indexed_db_for_origin

.. autofunction:: untrack_indexed_db_for_storage_key

Events
------

Generally, you do not need to instantiate CDP events
yourself. Instead, the API creates events for you and then
you use the event's attributes.

.. autoclass:: CacheStorageContentUpdated
      :members:
      :undoc-members:
      :exclude-members: from_json, to_json

.. autoclass:: CacheStorageListUpdated
      :members:
      :undoc-members:
      :exclude-members: from_json, to_json

.. autoclass:: IndexedDBContentUpdated
      :members:
      :undoc-members:
      :exclude-members: from_json, to_json

.. autoclass:: IndexedDBListUpdated
      :members:
      :undoc-members:
      :exclude-members: from_json, to_json

.. autoclass:: InterestGroupAccessed
      :members:
      :undoc-members:
      :exclude-members: from_json, to_json

.. autoclass:: SharedStorageAccessed
      :members:
      :undoc-members:
      :exclude-members: from_json, to_json

.. autoclass:: StorageBucketCreatedOrUpdated
      :members:
      :undoc-members:
      :exclude-members: from_json, to_json

.. autoclass:: StorageBucketDeleted
      :members:
      :undoc-members:
      :exclude-members: from_json, to_json

.. autoclass:: AttributionReportingSourceRegistered
      :members:
      :undoc-members:
      :exclude-members: from_json, to_json
