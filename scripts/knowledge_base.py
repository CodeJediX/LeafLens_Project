"""Plain-language field guidance shown alongside LeafLens predictions."""

PADDY_GUIDANCE = {
    "bacterial_leaf_blight": {
        "summary": "Water-soaked streaks often begin at the leaf edge, turn yellow, and can dry into pale lesions.",
        "actions": [
            "Avoid excess nitrogen and keep nutrition balanced.",
            "Improve drainage and avoid moving through wet fields.",
            "Use clean seed and resistant varieties in the next planting.",
            "Remove volunteer rice and infected residue after harvest.",
        ],
    },
    "bacterial_leaf_streak": {
        "summary": "Fine translucent streaks form between veins, later darkening and merging under humid conditions.",
        "actions": [
            "Use certified disease-free seed.",
            "Avoid damaging seedlings during transplanting.",
            "Apply nutrients evenly and avoid excess nitrogen.",
            "Rotate crops and remove infected residue where practical.",
        ],
    },
    "bacterial_panicle_blight": {
        "summary": "Florets discolor and grain filling is reduced, especially during hot, humid flowering periods.",
        "actions": [
            "Use clean, high-quality seed.",
            "Avoid late-season nitrogen applications.",
            "Adjust planting dates to reduce heat stress at flowering where possible.",
            "Confirm the diagnosis locally because chemical control options are limited.",
        ],
    },
    "blast": {
        "summary": "Diamond-shaped leaf lesions or neck damage may interrupt grain filling and weaken panicles.",
        "actions": [
            "Use locally recommended blast-resistant varieties.",
            "Maintain steady field moisture and avoid prolonged drying.",
            "Avoid excess nitrogen, especially split applications during risk periods.",
            "Ask an extension officer about approved fungicides and timing.",
        ],
    },
    "brown_spot": {
        "summary": "Small circular brown lesions are often associated with stressed plants or nutrient-poor soil.",
        "actions": [
            "Check soil fertility, especially potassium, before adding inputs.",
            "Maintain consistent irrigation and reduce drought stress.",
            "Use clean seed and an approved seed treatment for future planting.",
            "Manage infected residue after harvest.",
        ],
    },
    "dead_heart": {
        "summary": "A yellow, easily pulled central shoot is commonly associated with stem-borer feeding.",
        "actions": [
            "Remove and destroy affected tillers where infestation is limited.",
            "Use pheromone traps to monitor adult moth activity.",
            "Protect natural enemies and inspect nearby hills before treating.",
            "Use insecticides only at locally recommended thresholds and rates.",
        ],
    },
    "downy_mildew": {
        "summary": "Yellow streaking with pale growth on the leaf underside can spread quickly in damp fields.",
        "actions": [
            "Separate and remove severely affected plants.",
            "Improve airflow and field drainage.",
            "Start with clean seed in future plantings.",
            "Confirm locally before applying any fungicide.",
        ],
    },
    "hispa": {
        "summary": "Adults scrape the leaf surface while larvae mine within leaves, leaving pale linear damage.",
        "actions": [
            "Inspect several hills to estimate infestation before acting.",
            "Clip and destroy mined leaf tips when populations are low.",
            "Use sweep nets and conserve spiders and other natural predators.",
            "Treat only when local economic thresholds are exceeded.",
        ],
    },
    "normal": {
        "summary": "The image most closely matches the healthy-leaf class in the training set.",
        "actions": [
            "Continue regular scouting, including the underside of leaves.",
            "Maintain balanced nutrition and consistent irrigation.",
            "Photograph any new symptoms early so changes can be compared.",
        ],
    },
    "tungro": {
        "summary": "Yellow-orange discoloration and stunting may indicate a viral disease spread by green leafhoppers.",
        "actions": [
            "Mark and remove strongly affected plants to reduce the virus source.",
            "Monitor green leafhopper populations across the field.",
            "Use resistant varieties and synchronised planting where recommended.",
            "Consult an extension officer before vector-control treatment.",
        ],
    },
}


TEA_GUIDANCE = {
    "algal leaf": {
        "summary": "Velvety orange-brown patches are associated with red rust, which is favoured by humid, shaded conditions.",
        "actions": [
            "Prune to improve air movement and light penetration.",
            "Manage shade trees and drainage to reduce persistent moisture.",
            "Support plant vigour with balanced nutrition.",
            "Ask a local specialist whether a copper treatment is appropriate.",
        ],
    },
    "Anthracnose": {
        "summary": "Dark, expanding lesions may become sunken and are commonly more active during wet periods.",
        "actions": [
            "Remove heavily infected leaves and twigs from the field.",
            "Prune for airflow and avoid overhead wetting where possible.",
            "Improve drainage around affected bushes.",
            "Confirm locally before selecting a fungicide.",
        ],
    },
    "bird eye spot": {
        "summary": "Small round spots with a pale centre and darker border can resemble a bird's eye.",
        "actions": [
            "Check drainage and avoid waterlogged root zones.",
            "Review potassium and overall nutrition.",
            "Protect young plants from severe sun stress.",
            "Monitor new growth to see whether lesions are spreading.",
        ],
    },
    "brown blight": {
        "summary": "Large irregular brown patches, often on mature leaves, may lead to premature leaf drop.",
        "actions": [
            "Prune and remove affected material using clean tools.",
            "Open dense bushes to improve airflow.",
            "Avoid wounding plants during wet field work.",
            "Seek local advice on protection before heavy rain periods.",
        ],
    },
    "gray light": {
        "summary": "This label corresponds to gray blight-like lesions: pale grey areas that may contain tiny dark fruiting bodies.",
        "actions": [
            "Remove diseased material and sanitise pruning tools.",
            "Balance shade to reduce sun scorch and prolonged dampness.",
            "Improve overall plant health with measured nutrition.",
            "Have a local expert confirm the diagnosis before treatment.",
        ],
    },
    "healthy": {
        "summary": "The image most closely matches the healthy tea-leaf class in the training set.",
        "actions": [
            "Continue regular inspection and a consistent plucking schedule.",
            "Maintain balanced water, nutrition, and shade management.",
            "Keep this image as a baseline for future comparisons.",
        ],
    },
    "red leaf spot": {
        "summary": "Reddish-brown spotting can reduce active leaf area and may have several fungal or stress-related causes.",
        "actions": [
            "Prune to improve airflow through the bush.",
            "Avoid keeping leaves wet for long periods.",
            "Review soil and leaf nutrition for underlying stress.",
            "Confirm the cause before applying a broad-spectrum product.",
        ],
    },
    "white spot": {
        "summary": "Distinct pale lesions may resemble bird's-eye spot and need close inspection for a reliable field diagnosis.",
        "actions": [
            "Remove heavily affected leaves and clean tools between plants.",
            "Check drainage and nutrition for stress factors.",
            "Track whether symptoms spread to new growth.",
            "Seek confirmation before choosing a treatment.",
        ],
    },
}


GUIDANCE = {"paddy": PADDY_GUIDANCE, "tea": TEA_GUIDANCE}
