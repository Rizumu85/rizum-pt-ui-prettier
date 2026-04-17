// ==========================================
// Shader Name: Rizum_Anime_ToonShader_V12
// Description: Production Standard (White = Opaque, Black = Transparent).
// ==========================================

import lib-env.glsl
import lib-pbr.glsl
import lib-normal.glsl

// --- 0. 渲染状态控制 ---
//: state blend over

//: param custom { "default": false, "label": "Face Culling [背面剔除/单面显示]", "group": "General Settings [通用设置]" }
uniform_specialization bool u_enable_face_culling;

//: state cull_face on { "enable": "input.u_enable_face_culling" }
//: state cull_face off { "enable": "!input.u_enable_face_culling" }

// --- 1. 获取 SP 标准通道 (SamplerSparse) ---
//: param auto channel_basecolor
uniform SamplerSparse basecolor_tex;
//: param auto channel_opacity
uniform SamplerSparse opacity_tex;
//: param auto channel_user0
uniform SamplerSparse sdf_tex;
//: param auto channel_user1
uniform SamplerSparse shadowcolor_tex;
//: param auto channel_user2
uniform SamplerSparse custom_normal_tex;

// --- 2. 控制面板 (General Settings) ---
//: param custom { "default": [0.9098, 0.9098, 0.9098], "label": "Empty Color [默认底色]", "widget": "color", "group": "General Settings [通用设置]" }
uniform vec3 u_DefaultEmptyColor;

//: param custom { "default": [0.5, 0.5, 0.6], "label": "Shadow Tint [全局阴影色]", "widget": "color", "group": "General Settings [通用设置]" }
uniform vec3 u_GlobalShadowTint;

//: param custom { "default": false, "label": "Unlit Mode [无光照模式]", "group": "General Settings [通用设置]" }
uniform bool u_unlitMode;

// --- 3. 频道指南贴士 (Channel Guide) ---
//: param custom { "default": false, "label": "User0 -> SDF [脸部遮罩]", "group": "💡 Channel Guide [需在纹理集添加 User 通道]" }
uniform bool u_guide_user0;

//: param custom { "default": false, "label": "User1 -> SColor ShadowColor [阴影颜色]", "group": "💡 Channel Guide [需在纹理集添加 User 通道]" }
uniform bool u_guide_user1;

//: param custom { "default": false, "label": "User2 -> TNrm Toon Normal [自定义法线]", "group": "💡 Channel Guide [需在纹理集添加 User 通道]" }
uniform bool u_guide_user2;

void shade(V2F inputs)
{
    // ==========================================
    // 标准透明度逻辑 (配合 Opacity_Base 填充图层使用)
    // ==========================================
    vec4 opData = textureSparse(opacity_tex, inputs.sparse_coord);
    // 如果你没开 Opacity 通道，默认给 1.0 (实体)
    // 如果你开了通道，就严格读取通道里的数值 (需要你建一个白色填充图层垫底)
    float opacity = mix(1.0, opData.r, opData.a);

    vec4 baseColorData = textureSparse(basecolor_tex, inputs.sparse_coord);
    // Fix: Unpremultiply alpha first to recover the true painted hue (avoids dark/grey
    // fringing from premultiplied edge pixels), then naturally blend with the empty
    // background color using the original alpha so the edge transition looks correct
    // whether or not a background fill layer is present.
    vec3 trueColor = (baseColorData.a > 0.001)
        ? clamp(baseColorData.rgb / baseColorData.a, 0.0, 1.0)
        : u_DefaultEmptyColor;
    vec3 baseColor = mix(u_DefaultEmptyColor, trueColor, baseColorData.a);

    // [防优化废代码]
    if (u_guide_user0 || u_guide_user1 || u_guide_user2) { baseColor += 0.00001; }

    // 无光照模式 (Unlit)
    if (u_unlitMode) {
        alphaOutput(opacity);
        diffuseShadingOutput(baseColor);
        return; 
    }
    
    // 法线计算 (User2)
    vec3 normal;
    vec4 customNormalData = textureSparse(custom_normal_tex, inputs.sparse_coord);
    if (customNormalData.a > 0.0) {
        vec3 sampledNormal = customNormalData.xyz * 2.0 - 1.0;
        mat3 tbn = mat3(inputs.tangent, inputs.bitangent, inputs.normal);
        normal = normalize(tbn * sampledNormal);
    } else {
        normal = computeWSNormal(inputs.sparse_coord, inputs.tangent, inputs.bitangent, inputs.normal);
    }
    
    // 光线方向
    vec3 defaultLightVec = normalize(vec3(0.5, 0.5, 1.0)); 
    vec3 lightDir = normalize(environment_matrix * defaultLightVec);
    float shadowMask = 1.0;

    // 脸部 SDF 模式 (User0)
    vec4 sdfData = textureSparse(sdf_tex, inputs.sparse_coord);
    if (sdfData.a > 0.0) {
        float lightAngle = (lightDir.x + 1.0) * 0.5; 
        shadowMask = smoothstep(sdfData.r - 0.05, sdfData.r + 0.05, lightAngle); 
    } else {
        float NdotL = dot(normal, lightDir);
        shadowMask = smoothstep(-0.01, 0.01, NdotL); 
    }

    // 阴影颜色 (User1)
    vec3 finalShadowColor = u_GlobalShadowTint;
    vec4 paintedShadow = textureSparse(shadowcolor_tex, inputs.sparse_coord);
    if(paintedShadow.a > 0.0) { 
        finalShadowColor *= paintedShadow.rgb;
    }

    // 最终输出
    vec3 finalColor = mix(baseColor * finalShadowColor, baseColor, shadowMask);

    alphaOutput(opacity);
    diffuseShadingOutput(finalColor);
}