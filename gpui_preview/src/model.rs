#[derive(Clone, Copy)]
pub struct LayerItem {
    pub name: &'static str,
    pub kind: LayerKind,
    pub masked: bool,
    pub mapped: bool,
}

#[derive(Clone, Copy)]
pub enum LayerKind {
    Layer,
    Folder,
}

pub struct HostPanelData {
    pub title: &'static str,
    pub subtitle: &'static str,
    pub group_name: &'static str,
    pub group_subtitle: &'static str,
    pub items: Vec<LayerItem>,
    pub removable: bool,
}

pub struct PreviewData {
    pub source: HostPanelData,
    pub target: HostPanelData,
}

impl PreviewData {
    pub fn sample() -> Self {
        Self {
            source: HostPanelData {
                title: "SOURCE: PHOTOSHOP",
                subtitle: "BaseColor.psd",
                group_name: "Body Textures",
                group_subtitle: "3 Layers",
                items: vec![
                    LayerItem {
                        name: "Main_Layer",
                        kind: LayerKind::Layer,
                        masked: true,
                        mapped: false,
                    },
                    LayerItem {
                        name: "Details_Pass",
                        kind: LayerKind::Layer,
                        masked: false,
                        mapped: false,
                    },
                    LayerItem {
                        name: "Effects_Group",
                        kind: LayerKind::Folder,
                        masked: true,
                        mapped: false,
                    },
                ],
                removable: false,
            },
            target: HostPanelData {
                title: "TARGET: PAINTER",
                subtitle: "M_Body - BaseColor",
                group_name: "Target Group",
                group_subtitle: "1 Layer",
                items: vec![LayerItem {
                    name: "Dirt_Overlay",
                    kind: LayerKind::Layer,
                    masked: true,
                    mapped: true,
                }],
                removable: true,
            },
        }
    }
}
