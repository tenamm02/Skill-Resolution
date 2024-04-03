﻿/*
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * All rights reserved.
 *
 * Licensed under the Oculus SDK License Agreement (the "License");
 * you may not use the Oculus SDK except in compliance with the License,
 * which is provided at the time of installation or download, or which
 * otherwise accompanies this software in either electronic or hard copy form.
 *
 * You may obtain a copy of the License at
 *
 * https://developer.oculus.com/licenses/oculussdk/
 *
 * Unless required by applicable law or agreed to in writing, the Oculus SDK
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

using UnityEngine;

namespace Oculus.Interaction.DistanceReticles
{
    /// <summary>
    /// Part of the ghost hand reticle used for distance grabs. Attached to each GameObject that the ghost hand can interact with. Pairs with ReticleGhostDrawer.
    /// </summary>
    public class ReticleDataGhost : MonoBehaviour, IReticleData
    {
        /// <summary>
        /// The GameObject that the ghost hand can interact with.
        /// </summary>
        [Tooltip("The GameObject that the ghost hand can interact with.")]
        [SerializeField, Optional]
        private Transform _targetPoint;

        public Vector3 ProcessHitPoint(Vector3 hitPoint)
        {
            return _targetPoint != null ? _targetPoint.position
                : this.transform.position;
        }
    }
}
